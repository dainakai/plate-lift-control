"""Kinematic constants for the assembled calibration plate lift."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MotionConfig:
    """Mechanism and Tic motion parameters.

    Tic speed is expressed in microsteps per 10,000 seconds.  Acceleration is
    expressed in microsteps per 100 seconds per second.
    """

    screw_lead_mm: float = 1.5
    motor_full_steps_per_rev: int = 200
    microstep_divisor: int = 8
    travel_mm: float = 68.0
    approach_mm: float = 2.0
    nominal_bulk_speed_mm_s: float = 14.0625
    homing_towards_speed_mm_s: float = 6.0
    homing_away_speed_mm_s: float = 1.5
    acceleration_mm_s2: float = 31.25
    poll_interval_s: float = 0.20
    move_timeout_s: float = 20.0
    position_tolerance_steps: int = 16

    @property
    def microsteps_per_rev(self) -> int:
        return self.motor_full_steps_per_rev * self.microstep_divisor

    @property
    def microsteps_per_mm(self) -> float:
        return self.microsteps_per_rev / self.screw_lead_mm

    def mm_to_steps(self, distance_mm: float) -> int:
        return round(distance_mm * self.microsteps_per_mm)

    def speed_to_tic(self, speed_mm_s: float) -> int:
        return round(speed_mm_s * self.microsteps_per_mm * 10_000)

    def acceleration_to_tic(self, acceleration_mm_s2: float) -> int:
        return round(acceleration_mm_s2 * self.microsteps_per_mm * 100)

    @property
    def travel_steps(self) -> int:
        return self.mm_to_steps(self.travel_mm)

    @property
    def approach_steps(self) -> int:
        return self.mm_to_steps(self.approach_mm)

    @property
    def bulk_speed_tic(self) -> int:
        return self.speed_to_tic(self.nominal_bulk_speed_mm_s)

    @property
    def homing_towards_speed_tic(self) -> int:
        return self.speed_to_tic(self.homing_towards_speed_mm_s)

    @property
    def homing_away_speed_tic(self) -> int:
        return self.speed_to_tic(self.homing_away_speed_mm_s)

    @property
    def acceleration_tic(self) -> int:
        return self.acceleration_to_tic(self.acceleration_mm_s2)


DEFAULT_MOTION = MotionConfig()
