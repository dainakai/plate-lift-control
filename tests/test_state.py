from dataclasses import replace
from pathlib import Path

import pytest

from random_dot_plate_lift.models import Endpoint, TicStatus
from random_dot_plate_lift.state import StateStore


def status(uptime: float, serial: str = "A") -> TicStatus:
    return TicStatus(
        serial=serial,
        uptime_s=uptime,
        forward_limit_active=False,
        reverse_limit_active=False,
        energized=False,
        homing_active=False,
        current_position=0,
        position_uncertain=False,
        current_velocity=0,
        operation_state="De-energized",
    )


def test_state_is_trusted_only_for_same_device_boot(tmp_path: Path) -> None:
    store = StateStore(tmp_path)
    store.save(Endpoint.DOWN, status(100), homed=True)
    saved = store.load()

    assert store.trusted_endpoint(status(101), saved.observed_at_epoch_s + 1) == Endpoint.DOWN
    assert store.trusted_endpoint(status(1), saved.observed_at_epoch_s + 1) == Endpoint.UNKNOWN
    assert (
        store.trusted_endpoint(status(101, "B"), saved.observed_at_epoch_s + 1) == Endpoint.UNKNOWN
    )


def test_invalidated_state_is_unknown(tmp_path: Path) -> None:
    store = StateStore(tmp_path)
    store.save(Endpoint.UP, status(50), homed=True)
    store.invalidate(status(51))
    assert store.load().endpoint == Endpoint.UNKNOWN.value
    assert store.load().homed is False


def test_changed_stroke_invalidates_endpoint_but_keeps_shared_lock(tmp_path: Path) -> None:
    old = StateStore(tmp_path, travel_mm=50)
    new = StateStore(tmp_path, travel_mm=68)
    old.save(Endpoint.UP, status(100), homed=True)
    saved = old.load()

    assert old.lock_path == new.lock_path
    assert new.trusted_endpoint(status(101), saved.observed_at_epoch_s + 1) == Endpoint.UNKNOWN
    new.save(Endpoint.DOWN, status(102), homed=True)
    saved = new.load()
    assert saved.travel_mm == 68
    assert new.trusted_endpoint(status(103), saved.observed_at_epoch_s + 1) == Endpoint.DOWN
    assert old.trusted_endpoint(status(103), saved.observed_at_epoch_s + 1) == Endpoint.UNKNOWN


def test_legacy_state_without_stroke_is_only_trusted_for_50_mm(tmp_path: Path) -> None:
    import json

    old = StateStore(tmp_path, travel_mm=50)
    old.save(Endpoint.UP, status(100), homed=True)
    raw = json.loads(old.path.read_text())
    raw.pop("travel_mm")
    old.path.write_text(json.dumps(raw))

    now = raw["observed_at_epoch_s"] + 1
    assert old.trusted_endpoint(status(101), now) == Endpoint.UP
    assert StateStore(tmp_path, travel_mm=68).trusted_endpoint(status(101), now) == Endpoint.UNKNOWN


@pytest.mark.parametrize(
    "changes",
    [
        {"current_position": 1000},
        {"position_uncertain": True},
        {"current_velocity": 100},
        {"homing_active": True},
    ],
)
def test_manual_move_or_changed_device_state_invalidates_endpoint(tmp_path, changes) -> None:
    store = StateStore(tmp_path)
    store.save(Endpoint.DOWN, status(100), homed=True)
    now = store.load().observed_at_epoch_s + 1
    assert store.trusted_endpoint(replace(status(101), **changes), now) == Endpoint.UNKNOWN


def test_old_position_record_without_counter_is_not_reused(tmp_path) -> None:
    import json

    store = StateStore(tmp_path)
    store.save(Endpoint.DOWN, status(100), homed=True)
    raw = json.loads(store.path.read_text())
    raw.pop("current_position_steps")
    raw.pop("position_uncertain")
    store.path.write_text(json.dumps(raw))
    assert store.trusted_endpoint(status(101), raw["observed_at_epoch_s"] + 1) == Endpoint.UNKNOWN
