"""Deterministic Tic simulator for tests and CLI demonstrations."""

from __future__ import annotations

from .models import TicStatus
from .motion import DEFAULT_MOTION, MotionConfig


class MockTicBackend:
    name = "mock"

    def __init__(
        self,
        motion: MotionConfig = DEFAULT_MOTION,
        initial_position: int = 0,
        start_energized: bool = False,
    ) -> None:
        self.motion = motion
        self.position = initial_position
        self.target: int | None = None
        self.energized = start_energized
        self.safe_start = not start_energized
        self.homing_active = False
        self.homing_direction: str | None = None
        self.homing_phase = "idle"
        self.position_uncertain = False
        self.velocity = 0
        self.max_speed = motion.bulk_speed_tic
        self.uptime_s = 100.0
        self.command_timeout_resets = 0
        self.force_errors: tuple[str, ...] = ()
        self.freeze_motion = False

    def _tick(self) -> None:
        self.uptime_s += self.motion.poll_interval_s
        if not self.energized or self.freeze_motion:
            self.velocity = 0
            return

        if self.homing_active:
            sign = 1 if self.homing_direction == "fwd" else -1
            if self.homing_phase == "towards":
                step_size = max(
                    128,
                    int(
                        self.motion.homing_towards_speed_tic / 10_000 * self.motion.poll_interval_s
                    ),
                )
                self.velocity = sign * step_size
                self.position += sign * step_size
                reached = (
                    self.position >= self.motion.travel_steps + 128
                    if sign > 0
                    else self.position <= -128
                )
                if reached:
                    self.homing_phase = "away"
            else:
                step_size = max(
                    128,
                    int(self.motion.homing_away_speed_tic / 10_000 * self.motion.poll_interval_s),
                )
                self.velocity = -sign * step_size
                self.position -= sign * min(step_size, 256)
                self.homing_active = False
                self.homing_phase = "idle"
                self.position_uncertain = False
                self.position = 0  # This is the documented Tic homing result.
                self.velocity = 0
            return

        step_size = max(512, int(self.max_speed / 10_000 * self.motion.poll_interval_s))
        if self.target is None:
            self.velocity = 0
            return
        delta = self.target - self.position
        if abs(delta) <= step_size:
            self.position = self.target
            self.target = None
            self.velocity = 0
        else:
            sign = 1 if delta > 0 else -1
            self.position += sign * step_size
            self.velocity = sign * step_size

    def status(self) -> TicStatus:
        self._tick()
        errors: list[str] = list(self.force_errors)
        if not self.energized:
            errors.append("Intentionally de-energized")
        if self.safe_start:
            errors.append("Safe start violation")
        forward_active = (
            self.homing_active and self.homing_phase == "away" and (self.homing_direction == "fwd")
        )
        reverse_active = (
            self.homing_active and self.homing_phase == "away" and (self.homing_direction == "rev")
        )
        return TicStatus(
            serial="MOCK-3130",
            uptime_s=self.uptime_s,
            forward_limit_active=forward_active,
            reverse_limit_active=reverse_active,
            energized=self.energized,
            homing_active=self.homing_active,
            current_position=self.position,
            position_uncertain=self.position_uncertain,
            current_velocity=self.velocity,
            operation_state="Normal" if self.energized else "De-energized",
            errors_current=tuple(errors),
            errors_occurred=tuple(errors),
            vin_voltage=24.0,
        )

    def resume(self) -> None:
        self.energized = True
        self.safe_start = False

    def deenergize(self) -> None:
        self.energized = False
        self.safe_start = True
        self.target = None
        self.homing_active = False
        self.homing_phase = "idle"
        self.velocity = 0

    def reset_command_timeout(self) -> None:
        self.command_timeout_resets += 1

    def set_max_speed(self, value: int) -> None:
        self.max_speed = value

    def set_target_position(self, value: int) -> None:
        self.target = value

    def halt_and_set_position(self, value: int) -> None:
        self.position = value
        self.target = None
        self.velocity = 0
        self.position_uncertain = False

    def halt_and_hold(self) -> None:
        self.target = None
        self.velocity = 0

    def home(self, direction: str) -> None:
        if direction not in {"fwd", "rev"}:
            raise ValueError(direction)
        self.homing_direction = direction
        self.homing_phase = "towards"
        self.homing_active = True
        self.position_uncertain = True
