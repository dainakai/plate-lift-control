from dataclasses import replace
from pathlib import Path

import pytest

from random_dot_plate_lift.controller import PlateController
from random_dot_plate_lift.exceptions import MotionFault, MotionTimeout
from random_dot_plate_lift.experiment import safe_shutdown_on_exit
from random_dot_plate_lift.mock_backend import MockTicBackend
from random_dot_plate_lift.models import Endpoint, TicStatus
from random_dot_plate_lift.motion import DEFAULT_MOTION
from random_dot_plate_lift.state import StateStore
from random_dot_plate_lift.tic import parse_tic_status


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def monotonic(self) -> float:
        return self.value

    def sleep(self, seconds: float) -> None:
        self.value += seconds


def controller(tmp_path: Path, backend: MockTicBackend) -> PlateController:
    clock = FakeClock()
    return PlateController(
        backend=backend,
        store=StateStore(tmp_path),
        monotonic=clock.monotonic,
        sleep=clock.sleep,
    )


def test_unknown_position_homes_down_and_deenergizes(tmp_path: Path) -> None:
    backend = MockTicBackend(initial_position=20_000)
    ctl = controller(tmp_path, backend)

    result = ctl.move(Endpoint.DOWN)

    assert result.position == Endpoint.DOWN
    assert result.safe_to_service is True
    assert result.safe_to_unplug is True
    assert result.motor_energized is False
    assert backend.command_timeout_resets > 0


class TicTextErrorBackend(MockTicBackend):
    """Exercise the text decoder that the in-memory mock normally bypasses."""

    fault_during_homing = False

    def status(self) -> TicStatus:
        status = super().status()
        errors = status.errors_current
        if self.fault_during_homing and status.homing_active:
            errors = ("Low VIN",)
        rendered = "\n" + "".join(f"  - {error}\n" for error in errors) if errors else "None\n"
        decoded = parse_tic_status("Errors currently stopping the motor: " + rendered)
        return replace(status, errors_current=decoded.errors_current, vin_voltage=21.2)


def test_tic_none_text_allows_r10_homing_to_finish(tmp_path: Path) -> None:
    motion = replace(DEFAULT_MOTION, travel_mm=68, move_timeout_s=20)
    backend = TicTextErrorBackend(motion=motion, initial_position=20_000)
    clock = FakeClock()
    ctl = PlateController(
        backend,
        StateStore(tmp_path, travel_mm=68),
        motion,
        monotonic=clock.monotonic,
        sleep=clock.sleep,
    )

    result = ctl.move(Endpoint.DOWN)

    assert result.position == Endpoint.DOWN
    assert result.motor_energized is False
    assert result.fault == ()
    assert result.safe_to_unplug is True


def test_tic_real_fault_during_homing_still_deenergizes(tmp_path: Path) -> None:
    backend = TicTextErrorBackend(initial_position=20_000)
    backend.fault_during_homing = True
    ctl = controller(tmp_path, backend)

    with pytest.raises(MotionFault, match="fault during homing: Low VIN"):
        ctl.move(Endpoint.DOWN)

    assert backend.energized is False
    assert ctl.store.load().endpoint == Endpoint.UNKNOWN.value


def test_known_down_bulk_moves_then_homes_up(tmp_path: Path) -> None:
    backend = MockTicBackend(initial_position=0)
    ctl = controller(tmp_path, backend)
    ctl.move(Endpoint.DOWN)

    result = ctl.move(Endpoint.UP)

    assert result.position == Endpoint.UP
    assert result.current_position_steps == DEFAULT_MOTION.travel_steps
    assert result.safe_to_image is True
    assert result.safe_to_service is False
    assert backend.energized is False


def test_shutdown_always_ends_down_and_off(tmp_path: Path) -> None:
    backend = MockTicBackend(initial_position=DEFAULT_MOTION.travel_steps)
    ctl = controller(tmp_path, backend)
    ctl.move(Endpoint.UP)

    result = ctl.shutdown()

    assert result.position == Endpoint.DOWN
    assert result.safe_to_unplug is True
    assert result.motor_energized is False


def test_explicit_home_does_not_skip_a_trusted_down_endpoint(tmp_path: Path) -> None:
    backend = MockTicBackend(initial_position=1000)
    ctl = controller(tmp_path, backend)
    ctl.move(Endpoint.DOWN)
    backend.homing_direction = None

    result = ctl.move(Endpoint.DOWN, force_home=True)

    assert backend.homing_direction == "rev"
    assert result.position == Endpoint.DOWN
    assert result.safe_to_unplug is True


def test_unexpected_fault_fails_closed(tmp_path: Path) -> None:
    backend = MockTicBackend()
    backend.force_errors = ("Motor driver error",)
    ctl = controller(tmp_path, backend)

    with pytest.raises(MotionFault, match="Motor driver error"):
        ctl.move(Endpoint.UP)

    assert backend.energized is False
    assert ctl.store.load().endpoint == Endpoint.UNKNOWN.value


def test_timeout_deenergizes_and_invalidates(tmp_path: Path) -> None:
    backend = MockTicBackend(initial_position=25_000)
    backend.freeze_motion = True
    fast_timeout = replace(DEFAULT_MOTION, move_timeout_s=0.6)
    clock = FakeClock()
    ctl = PlateController(
        backend=backend,
        store=StateStore(tmp_path),
        motion=fast_timeout,
        monotonic=clock.monotonic,
        sleep=clock.sleep,
    )

    with pytest.raises(MotionTimeout):
        ctl.move(Endpoint.DOWN)

    assert backend.energized is False
    assert ctl.store.load().endpoint == Endpoint.UNKNOWN.value


class BothLimitsBackend(MockTicBackend):
    def status(self) -> TicStatus:
        return replace(
            super().status(),
            forward_limit_active=True,
            reverse_limit_active=True,
        )


def test_both_limits_refuses_motion(tmp_path: Path) -> None:
    ctl = controller(tmp_path, BothLimitsBackend())
    with pytest.raises(MotionFault, match="both NC endpoint inputs"):
        ctl.move(Endpoint.UP)


class InterruptingBackend(MockTicBackend):
    interrupt_on_resume = False

    def resume(self) -> None:
        super().resume()
        if self.interrupt_on_resume:
            raise KeyboardInterrupt


def test_interrupted_motion_deenergizes_and_leaves_unknown(tmp_path: Path) -> None:
    backend = InterruptingBackend()
    ctl = controller(tmp_path, backend)
    ctl.move(Endpoint.DOWN)
    backend.interrupt_on_resume = True

    with pytest.raises(KeyboardInterrupt):
        ctl.move(Endpoint.UP)

    assert backend.energized is False
    assert ctl.store.load().endpoint == Endpoint.UNKNOWN.value


def test_experiment_context_shutdowns_even_after_exception(tmp_path: Path) -> None:
    backend = MockTicBackend()
    ctl = controller(tmp_path, backend)

    with (
        pytest.raises(RuntimeError, match="camera failed"),
        safe_shutdown_on_exit(ctl),
    ):
        ctl.move(Endpoint.UP)
        raise RuntimeError("camera failed")

    result = ctl.public_status()
    assert result.position == Endpoint.DOWN
    assert result.safe_to_unplug is True


@pytest.mark.parametrize("error", [MotionFault("limit fault"), KeyboardInterrupt()])
def test_experiment_does_not_move_again_after_motion_error_or_interrupt(tmp_path, error) -> None:
    backend = MockTicBackend()
    ctl = controller(tmp_path, backend)
    ctl.move(Endpoint.UP)
    before = backend.command_timeout_resets

    with pytest.raises(type(error)), safe_shutdown_on_exit(ctl):
        raise error

    assert backend.command_timeout_resets == before
    assert backend.energized is False
