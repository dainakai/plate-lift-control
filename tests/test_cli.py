import json
from pathlib import Path

from random_dot_plate_lift.cli import run


def test_json_status_is_machine_readable(tmp_path: Path, capsys) -> None:
    result = run(
        [
            "status",
            "--backend",
            "mock",
            "--state-dir",
            str(tmp_path),
            "--json",
        ]
    )
    output = json.loads(capsys.readouterr().out)
    assert result == 0
    assert output["ok"] is True
    assert output["backend"] == "mock"
    assert output["position"] == "UNKNOWN"
    assert output["safe_to_image"] is False


def test_home_command_reports_safe_to_unplug(tmp_path: Path, capsys) -> None:
    result = run(
        [
            "home",
            "--backend",
            "mock",
            "--state-dir",
            str(tmp_path),
            "--json",
        ]
    )
    output = json.loads(capsys.readouterr().out)
    assert result == 0
    assert output["position"] == "DOWN"
    assert output["safe_to_unplug"] is True


def test_r10_cli_uses_68_mm_and_records_stroke(tmp_path: Path, capsys, monkeypatch) -> None:
    from random_dot_plate_lift import cli
    from random_dot_plate_lift.mock_backend import MockTicBackend
    from random_dot_plate_lift.motion import MotionConfig
    from random_dot_plate_lift.state import StateStore

    motion = MotionConfig(travel_mm=68, move_timeout_s=20)
    backend = MockTicBackend(motion=motion, initial_position=motion.travel_steps)
    monkeypatch.setattr(cli, "MockTicBackend", lambda motion: backend)
    args = ["--backend", "mock", "--travel-mm", "68", "--state-dir", str(tmp_path), "--json"]
    assert run(["home", *args]) == 0
    home = json.loads(capsys.readouterr().out)
    assert home["position"] == "DOWN"
    assert run(["up", *args]) == 0
    up = json.loads(capsys.readouterr().out)
    assert up["position"] == "UP"
    assert up["current_position_steps"] == 72533
    assert StateStore(tmp_path, travel_mm=68).load().travel_mm == 68


def test_default_stroke_matches_assembled_device(tmp_path: Path, capsys) -> None:
    from random_dot_plate_lift.state import StateStore

    assert run(["home", "--backend", "mock", "--state-dir", str(tmp_path)]) == 0
    assert StateStore(tmp_path).load().travel_mm == 68


def test_legacy_50_mm_stroke_remains_available(tmp_path: Path, capsys) -> None:
    from random_dot_plate_lift.state import StateStore

    assert (
        run(["home", "--backend", "mock", "--state-dir", str(tmp_path), "--travel-mm", "50"]) == 0
    )
    assert StateStore(tmp_path, travel_mm=50).load().travel_mm == 50
