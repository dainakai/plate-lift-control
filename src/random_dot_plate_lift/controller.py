"""Fail-closed two-position motion controller."""

from __future__ import annotations

import time
from collections.abc import Callable

from .exceptions import MotionFault, MotionTimeout
from .models import Endpoint, LimitState, PublicStatus, TicStatus
from .motion import DEFAULT_MOTION, MotionConfig
from .state import StateStore
from .tic import TicBackend

IDLE_EXPECTED_ERRORS = {
    "Intentionally de-energized",
    "Safe start violation",
    "Command timeout",
}


def unexpected_errors(status: TicStatus) -> tuple[str, ...]:
    expected = IDLE_EXPECTED_ERRORS if not status.energized and status.stopped else set()
    return tuple(error for error in status.errors_current if error not in expected)


class PlateController:
    def __init__(
        self,
        backend: TicBackend,
        store: StateStore,
        motion: MotionConfig = DEFAULT_MOTION,
        monotonic: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.backend = backend
        self.store = store
        self.motion = motion
        self.monotonic = monotonic
        self.sleep = sleep

    def _position_from_evidence(self, status: TicStatus) -> tuple[Endpoint, bool]:
        if status.limit == LimitState.BOTH:
            return Endpoint.UNKNOWN, False
        if status.limit == LimitState.UP and status.stopped:
            return Endpoint.UP, True
        if status.limit == LimitState.DOWN and status.stopped:
            return Endpoint.DOWN, True
        endpoint = self.store.trusted_endpoint(status)
        return endpoint, endpoint != Endpoint.UNKNOWN

    def public_status(self) -> PublicStatus:
        raw = self.backend.status()
        endpoint, homed = self._position_from_evidence(raw)
        faults = list(unexpected_errors(raw))
        if raw.limit == LimitState.BOTH:
            faults.append("both endpoint limits are active")
        stopped_and_off = raw.stopped and not raw.energized
        safe_common = stopped_and_off and homed and not faults
        return PublicStatus(
            backend=self.backend.name,
            device_serial=raw.serial,
            position=endpoint,
            limit=raw.limit,
            motor_energized=raw.energized,
            moving=not raw.stopped,
            homed=homed,
            fault=tuple(faults),
            safe_to_image=safe_common and endpoint in {Endpoint.DOWN, Endpoint.UP},
            safe_to_service=safe_common and endpoint == Endpoint.DOWN,
            safe_to_unplug=safe_common and endpoint == Endpoint.DOWN,
            current_position_steps=raw.current_position,
            vin_voltage=raw.vin_voltage,
        )

    def move(self, target: Endpoint, *, force_home: bool = False) -> PublicStatus:
        if target not in {Endpoint.DOWN, Endpoint.UP}:
            raise ValueError("target must be DOWN or UP")
        initial = self.backend.status()
        if initial.limit == LimitState.BOTH:
            self.store.invalidate(initial)
            raise MotionFault("both NC endpoint inputs are active; check wiring before motion")
        faults = unexpected_errors(initial)
        if faults:
            self.store.invalidate(initial)
            raise MotionFault("Tic reports a blocking fault: " + "; ".join(faults))

        known, _ = self._position_from_evidence(initial)
        if known == target and initial.stopped and not force_home:
            self.backend.deenergize()
            final = self.backend.status()
            self.store.save(target, final, homed=True)
            return self.public_status()

        # From this point onward a process crash must not leave stale endpoint
        # evidence.  Only a completed homing procedure writes a known endpoint.
        self.store.invalidate(initial)
        try:
            deadline = self.monotonic() + self.motion.move_timeout_s
            self.backend.set_max_speed(self.motion.bulk_speed_tic)
            self.backend.resume()
            self.backend.reset_command_timeout()

            if known in {Endpoint.DOWN, Endpoint.UP} and not force_home:
                start_steps = 0 if known == Endpoint.DOWN else self.motion.travel_steps
                self.backend.halt_and_set_position(start_steps)
                approach = (
                    self.motion.travel_steps - self.motion.approach_steps
                    if target == Endpoint.UP
                    else self.motion.approach_steps
                )
                self.backend.set_target_position(approach)
                self._wait_for_position(approach, target, deadline)

            # When position is unknown, homing covers the whole travel at 6 mm/s.
            # When known, it covers only the final 2 mm after the bulk move.
            direction = "fwd" if target == Endpoint.UP else "rev"
            self.backend.home(direction)
            self._wait_for_homing(target, deadline)

            # Tic homing ends just after the switch releases and labels that point 0.
            # Relabel the upper endpoint to +travel without moving it.
            endpoint_steps = self.motion.travel_steps if target == Endpoint.UP else 0
            self.backend.halt_and_set_position(endpoint_steps)
            self.backend.deenergize()
            final = self.backend.status()
            final_faults = unexpected_errors(final)
            if final_faults or not final.stopped or final.energized:
                raise MotionFault("endpoint did not settle safely: " + "; ".join(final_faults))
            self.store.save(target, final, homed=True)
            return self.public_status()
        except BaseException:
            try:
                self.backend.deenergize()
                stopped = self.backend.status()
                self.store.invalidate(stopped)
            except Exception:
                self.store.invalidate()
            raise

    def shutdown(self) -> PublicStatus:
        result = self.move(Endpoint.DOWN)
        if not result.safe_to_unplug:
            raise MotionFault("shutdown ended without safe_to_unplug confirmation")
        return result

    def _wait_for_position(self, target_steps: int, endpoint: Endpoint, deadline: float) -> None:
        while True:
            self.backend.reset_command_timeout()
            status = self.backend.status()
            faults = unexpected_errors(status)
            if faults:
                raise MotionFault("fault during bulk move: " + "; ".join(faults))
            if status.limit == LimitState.BOTH:
                raise MotionFault("both endpoint limits became active during motion")
            destination_limit = LimitState.UP if endpoint == Endpoint.UP else LimitState.DOWN
            if status.limit == destination_limit:
                raise MotionFault("destination limit activated before the homing approach")
            if (
                abs(status.current_position - target_steps) <= self.motion.position_tolerance_steps
                and status.current_velocity == 0
            ):
                return
            if self.monotonic() >= deadline:
                raise MotionTimeout(
                    f"bulk move exceeded the {self.motion.move_timeout_s:g} s safety limit"
                )
            self.sleep(self.motion.poll_interval_s)

    def _wait_for_homing(self, endpoint: Endpoint, deadline: float) -> None:
        saw_homing = False
        while True:
            self.backend.reset_command_timeout()
            status = self.backend.status()
            faults = unexpected_errors(status)
            if faults:
                raise MotionFault("fault during homing: " + "; ".join(faults))
            if status.limit == LimitState.BOTH:
                raise MotionFault("both endpoint limits became active during homing")
            saw_homing = saw_homing or status.homing_active or status.position_uncertain
            if saw_homing and not status.homing_active and not status.position_uncertain:
                return
            if self.monotonic() >= deadline:
                name = endpoint.value.lower()
                raise MotionTimeout(
                    f"{name} homing did not finish within {self.motion.move_timeout_s:g} s"
                )
            self.sleep(self.motion.poll_interval_s)
