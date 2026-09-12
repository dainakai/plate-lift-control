"""Calibrate with the plate raised, then acquire with the plate lowered.

Default: a mock run with no USB access. Pass --backend ticcmd for the device.
Replace capture_calibration() and capture_sample() with the camera calls.
"""

from __future__ import annotations

import argparse
import tempfile
import time
from contextlib import nullcontext
from pathlib import Path

from filelock import FileLock, Timeout

from random_dot_plate_lift.controller import PlateController
from random_dot_plate_lift.exceptions import PlateLiftError
from random_dot_plate_lift.experiment import safe_shutdown_on_exit
from random_dot_plate_lift.mock_backend import MockTicBackend
from random_dot_plate_lift.models import Endpoint, PublicStatus
from random_dot_plate_lift.motion import MotionConfig
from random_dot_plate_lift.state import StateStore
from random_dot_plate_lift.tic import SubprocessTicBackend


def capture_calibration(cycle: int) -> None:
    # Replace this print with your calibration image acquisition.
    print(f"cycle {cycle}: UP / calibration capture goes here", flush=True)


def capture_sample(cycle: int) -> None:
    # Replace this print with your sample image acquisition.
    print(f"cycle {cycle}: DOWN / sample capture goes here", flush=True)


def require_image_position(status: PublicStatus, endpoint: Endpoint) -> None:
    if not status.safe_to_image or status.position != endpoint:
        raise PlateLiftError(f"plate did not settle at {endpoint}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=["mock", "ticcmd"], default="mock")
    parser.add_argument("--cycles", type=int, default=1)
    parser.add_argument("--settle-seconds", type=float, default=0.5)
    parser.add_argument("--travel-mm", type=int, choices=[50, 68], default=68)
    parser.add_argument("--serial")
    parser.add_argument("--ticcmd", default="ticcmd")
    args = parser.parse_args()
    if args.cycles < 1 or not 0 <= args.settle_seconds <= 60:
        parser.error("cycles must be positive and settle-seconds must be between 0 and 60")

    motion = MotionConfig(
        travel_mm=args.travel_mm, move_timeout_s=20 if args.travel_mm == 68 else 10
    )
    mock = args.backend == "mock"
    state_context = (
        tempfile.TemporaryDirectory(prefix="plate-lift-demo-") if mock else nullcontext()
    )
    with state_context as directory:
        store = StateStore(Path(directory) if directory else None, travel_mm=args.travel_mm)
        store.directory.mkdir(parents=True, exist_ok=True)
        backend = (
            MockTicBackend(motion=motion)
            if mock
            else SubprocessTicBackend(executable=args.ticcmd, serial=args.serial)
        )
        controller = PlateController(
            backend, store, motion, sleep=(lambda seconds: None) if mock else time.sleep
        )
        try:
            # Share the same lock as platectl for the entire acquisition sequence.
            with FileLock(store.lock_path, timeout=0), safe_shutdown_on_exit(controller):
                print(f"backend: {args.backend}", flush=True)
                controller.move(Endpoint.DOWN, force_home=True)
                for cycle in range(1, args.cycles + 1):
                    require_image_position(controller.move(Endpoint.UP), Endpoint.UP)
                    if not mock:
                        time.sleep(args.settle_seconds)
                    capture_calibration(cycle)
                    require_image_position(controller.move(Endpoint.DOWN), Endpoint.DOWN)
                    if not mock:
                        time.sleep(args.settle_seconds)
                    capture_sample(cycle)
        except Timeout:
            print("another platectl command or experiment is already running")
            return 5
        except PlateLiftError as exc:
            print(f"motion stopped: {exc}; inspect the device before retrying")
            return exc.exit_code
        except KeyboardInterrupt:
            print("interrupted; no automatic return move")
            return 130
        print("finished: DOWN / motor off", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
