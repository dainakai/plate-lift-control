import pytest

from random_dot_plate_lift.exceptions import HardwareConnectionError
from random_dot_plate_lift.tic import parse_tic_status

SAMPLE = """
Name:                         Tic T825
Serial number:                00420001
Up time:                      1:02:05
Forward limit active:         No
Reverse limit active:         Yes
VIN voltage:                  24.015 V
Operation state:              De-energized
Energized:                    No
Homing active:                No
Current position:             0
Position uncertain:           No
Current velocity:             0
Errors currently stopping the motor:
  - Intentionally de-energized
  - Safe start violation
Errors that occurred since last check: []
"""


def test_parse_official_status_yaml_shape() -> None:
    status = parse_tic_status(SAMPLE)
    assert status.serial == "00420001"
    assert status.uptime_s == 3725
    assert status.reverse_limit_active is True
    assert status.forward_limit_active is False
    assert status.energized is False
    assert status.current_position == 0
    assert status.vin_voltage == 24.015
    assert status.errors_current == (
        "Intentionally de-energized",
        "Safe start violation",
    )


@pytest.mark.parametrize(
    ("error_value", "expected"),
    [
        ("None", ()),
        ('"None"', ()),
        ("[]", ()),
        ("null", ()),
        ("", ()),
        ("Low VIN", ("Low VIN",)),
        ("\n  - Low VIN", ("Low VIN",)),
        (
            "\n  - Low VIN\n  - Motor driver error",
            ("Low VIN", "Motor driver error"),
        ),
        ("Unrecognized firmware error", ("Unrecognized firmware error",)),
    ],
)
def test_error_fields_accept_none_or_errors_without_splitting_characters(
    error_value: str, expected: tuple[str, ...]
) -> None:
    text = (
        "Energized: Yes\n"
        "Homing active: Yes\n"
        "Current velocity: -6400\n"
        "VIN voltage: 21.200 V\n"
        f"Errors currently stopping the motor: {error_value}\n"
        f"Errors that occurred since last check: {error_value}\n"
    )

    status = parse_tic_status(text)

    assert status.errors_current == expected
    assert status.errors_occurred == expected
    assert status.vin_voltage == 21.2


@pytest.mark.parametrize(
    "field",
    [
        "Errors currently stopping the motor",
        "Errors that occurred since last check",
    ],
)
@pytest.mark.parametrize("value", ["true", "0", "{unexpected: None}", "[null]"])
def test_malformed_error_fields_are_not_treated_as_no_errors(field: str, value: str) -> None:
    with pytest.raises(HardwareConnectionError, match="malformed.*error"):
        parse_tic_status(f"{field}: {value}\n")
