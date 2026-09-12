"""Typed controller state exposed by the CLI."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class Endpoint(StrEnum):
    DOWN = "DOWN"
    UP = "UP"
    UNKNOWN = "UNKNOWN"


class LimitState(StrEnum):
    NONE = "none"
    DOWN = "down"
    UP = "up"
    BOTH = "both"


@dataclass(frozen=True)
class TicStatus:
    serial: str
    uptime_s: float
    forward_limit_active: bool
    reverse_limit_active: bool
    energized: bool
    homing_active: bool
    current_position: int
    position_uncertain: bool
    current_velocity: int
    operation_state: str
    errors_current: tuple[str, ...] = ()
    errors_occurred: tuple[str, ...] = ()
    vin_voltage: float | None = None

    @property
    def stopped(self) -> bool:
        return not self.homing_active and self.current_velocity == 0

    @property
    def limit(self) -> LimitState:
        if self.forward_limit_active and self.reverse_limit_active:
            return LimitState.BOTH
        if self.forward_limit_active:
            return LimitState.UP
        if self.reverse_limit_active:
            return LimitState.DOWN
        return LimitState.NONE


@dataclass(frozen=True)
class PublicStatus:
    backend: str
    device_serial: str
    position: Endpoint
    limit: LimitState
    motor_energized: bool
    moving: bool
    homed: bool
    fault: tuple[str, ...]
    safe_to_image: bool
    safe_to_service: bool
    safe_to_unplug: bool
    current_position_steps: int
    vin_voltage: float | None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["position"] = self.position.value
        result["limit"] = self.limit.value
        result["fault"] = list(self.fault)
        return result
