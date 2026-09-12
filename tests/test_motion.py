from random_dot_plate_lift.motion import DEFAULT_MOTION


def test_mechanism_conversion() -> None:
    motion = DEFAULT_MOTION
    assert motion.microsteps_per_rev == 1600
    assert motion.microsteps_per_mm == 1600 / 1.5
    assert motion.travel_steps == 72_533
    assert motion.approach_steps == 2_133
    assert motion.bulk_speed_tic == 150_000_000
    assert motion.homing_towards_speed_tic == 64_000_000
    assert motion.homing_away_speed_tic == 16_000_000
    assert motion.acceleration_tic == 3_333_333
