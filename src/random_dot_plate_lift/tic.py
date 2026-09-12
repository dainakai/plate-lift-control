"""Pololu Tic backend implemented through the official ``ticcmd`` utility."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from typing import Any, Protocol

import yaml

from .exceptions import HardwareConnectionError
from .models import TicStatus


class TicBackend(Protocol):
    name: str

    def status(self) -> TicStatus: ...

    def resume(self) -> None: ...

    def deenergize(self) -> None: ...

    def reset_command_timeout(self) -> None: ...

    def set_max_speed(self, value: int) -> None: ...

    def set_target_position(self, value: int) -> None: ...

    def halt_and_set_position(self, value: int) -> None: ...

    def halt_and_hold(self) -> None: ...

    def home(self, direction: str) -> None: ...


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"yes", "true", "1", "active"}


def _as_number(value: Any, default: float = 0.0) -> float:
    if isinstance(value, int | float):
        return float(value)
    match = re.search(r"[-+]?\d+(?:\.\d+)?", str(value))
    return float(match.group()) if match else default


def _uptime_seconds(value: Any) -> float:
    # PyYAML 1.1 parses 1:02:05 as the base-60 integer 3725.
    if isinstance(value, int | float):
        return float(value)
    fields = str(value).strip().split(":")
    try:
        total = 0.0
        for field in fields:
            total = total * 60 + float(field)
        return total
    except ValueError:
        return 0.0


def _parse_errors(value: Any, field: str) -> tuple[str, ...]:
    """ticcmd prints the scalar ``None`` when there are no errors."""

    if value is None:
        return ()
    if isinstance(value, str):
        error = value.strip()
        return () if error in {"", "None"} else (error,)
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(value)
    raise HardwareConnectionError(f"ticcmd returned malformed error field: {field}")


def parse_tic_status(text: str) -> TicStatus:
    """Parse ``ticcmd --status --full`` YAML without relying on key order."""

    # YAML 1.1 treats digit-only values with a leading zero as octal.  Tic USB
    # serial numbers are identifiers, so preserve the exact text from ticcmd.
    serial_match = re.search(r"(?m)^Serial number:\s*(\S+)\s*$", text)
    raw = yaml.safe_load(text)
    if not isinstance(raw, dict):
        raise HardwareConnectionError("ticcmd returned malformed status output")

    current_error_field = "Errors currently stopping the motor"
    occurred_error_field = "Errors that occurred since last check"
    return TicStatus(
        serial=serial_match.group(1) if serial_match else str(raw.get("Serial number", "unknown")),
        uptime_s=_uptime_seconds(raw.get("Up time", 0)),
        forward_limit_active=_as_bool(raw.get("Forward limit active", False)),
        reverse_limit_active=_as_bool(raw.get("Reverse limit active", False)),
        energized=_as_bool(raw.get("Energized", False)),
        homing_active=_as_bool(raw.get("Homing active", False)),
        current_position=int(_as_number(raw.get("Current position", 0))),
        position_uncertain=_as_bool(raw.get("Position uncertain", True)),
        current_velocity=int(_as_number(raw.get("Current velocity", 0))),
        operation_state=str(raw.get("Operation state", "Unknown")),
        errors_current=_parse_errors(raw.get(current_error_field), current_error_field),
        errors_occurred=_parse_errors(raw.get(occurred_error_field), occurred_error_field),
        vin_voltage=(
            _as_number(raw["VIN voltage"]) if raw.get("VIN voltage") is not None else None
        ),
    )


class SubprocessTicBackend:
    """Wrapper around Pololu's CLI for Windows, macOS, and Linux."""

    name = "ticcmd"

    def __init__(
        self,
        executable: str | Path = "ticcmd",
        serial: str | None = None,
        command_timeout_s: float = 5.0,
    ) -> None:
        self.executable = str(executable)
        self.serial = serial
        self.command_timeout_s = command_timeout_s

    def _run(self, *args: str, timeout_s: float | None = None) -> str:
        command = [self.executable]
        if self.serial:
            command.extend(["--serial", self.serial])
        command.extend(args)
        try:
            completed = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout_s or self.command_timeout_s,
            )
        except FileNotFoundError as exc:
            raise HardwareConnectionError(
                "ticcmd was not found; install the Pololu Tic software and add it to PATH"
            ) from exc
        except subprocess.TimeoutExpired as exc:
            raise HardwareConnectionError(f"ticcmd timed out: {' '.join(command)}") from exc
        if completed.returncode != 0:
            detail = completed.stderr.strip() or completed.stdout.strip() or "unknown ticcmd error"
            raise HardwareConnectionError(f"ticcmd failed: {detail}")
        return completed.stdout

    def status(self) -> TicStatus:
        return parse_tic_status(self._run("--status", "--full"))

    def resume(self) -> None:
        self._run("--resume")

    def deenergize(self) -> None:
        self._run("--deenergize")

    def reset_command_timeout(self) -> None:
        self._run("--reset-command-timeout")

    def set_max_speed(self, value: int) -> None:
        self._run("--max-speed", str(value))

    def set_target_position(self, value: int) -> None:
        self._run("--position", str(value))

    def halt_and_set_position(self, value: int) -> None:
        self._run("--halt-and-set-position", str(value))

    def halt_and_hold(self) -> None:
        self._run("--halt-and-hold")

    def home(self, direction: str) -> None:
        if direction not in {"fwd", "rev"}:
            raise ValueError(f"invalid Tic homing direction: {direction}")
        self._run("--home", direction)
