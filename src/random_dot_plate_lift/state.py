"""Conservative persisted position evidence."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from platformdirs import user_state_path

from .models import Endpoint, TicStatus
from .motion import DEFAULT_MOTION


@dataclass
class PersistentState:
    endpoint: str = Endpoint.UNKNOWN.value
    device_serial: str = ""
    device_uptime_s: float = 0.0
    observed_at_epoch_s: float = 0.0
    homed: bool = False
    travel_mm: float = 50.0
    current_position_steps: int | None = None
    position_uncertain: bool | None = None


class StateStore:
    def __init__(
        self, directory: Path | None = None, travel_mm: float = DEFAULT_MOTION.travel_mm
    ) -> None:
        self.travel_mm = travel_mm
        self.directory = directory or user_state_path(
            appname="random-dot-plate-lift", appauthor="dainakai"
        )
        self.path = self.directory / "state.json"
        self.lock_path = self.directory / "command.lock"

    def load(self) -> PersistentState:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return PersistentState(**raw)
        except (FileNotFoundError, json.JSONDecodeError, TypeError):
            return PersistentState()

    def save(self, endpoint: Endpoint, status: TicStatus, homed: bool) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        state = PersistentState(
            endpoint=endpoint.value,
            device_serial=status.serial,
            device_uptime_s=status.uptime_s,
            observed_at_epoch_s=time.time(),
            homed=homed,
            travel_mm=self.travel_mm,
            current_position_steps=status.current_position,
            position_uncertain=status.position_uncertain,
        )
        temporary = self.path.with_suffix(".tmp")
        temporary.write_text(json.dumps(asdict(state), indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.path)

    def invalidate(self, status: TicStatus | None = None) -> None:
        if status is None:
            status = TicStatus(
                serial="",
                uptime_s=0,
                forward_limit_active=False,
                reverse_limit_active=False,
                energized=False,
                homing_active=False,
                current_position=0,
                position_uncertain=True,
                current_velocity=0,
                operation_state="Unknown",
            )
        self.save(Endpoint.UNKNOWN, status, homed=False)

    def trusted_endpoint(self, status: TicStatus, now_epoch_s: float | None = None) -> Endpoint:
        """Reuse an endpoint only while boot, counter, and uncertainty still match.

        The counter check detects most intervening manual moves in Tic Control
        Center. It cannot detect physical motion while the motor is unpowered.
        """

        state = self.load()
        if state.travel_mm != self.travel_mm:
            return Endpoint.UNKNOWN
        if not state.homed or state.device_serial != status.serial:
            return Endpoint.UNKNOWN
        if (
            state.current_position_steps != status.current_position
            or state.position_uncertain is None
            or state.position_uncertain != status.position_uncertain
            or not status.stopped
        ):
            return Endpoint.UNKNOWN
        now = time.time() if now_epoch_s is None else now_epoch_s
        wall_elapsed = max(0.0, now - state.observed_at_epoch_s)
        device_elapsed = status.uptime_s - state.device_uptime_s
        if device_elapsed < -0.5 or abs(device_elapsed - wall_elapsed) > 5.0:
            return Endpoint.UNKNOWN
        try:
            return Endpoint(state.endpoint)
        except ValueError:
            return Endpoint.UNKNOWN
