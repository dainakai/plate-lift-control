"""User-facing ``platectl`` command."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from filelock import FileLock, Timeout

from .controller import PlateController
from .exceptions import ConcurrentCommandError, PlateLiftError
from .mock_backend import MockTicBackend
from .models import Endpoint, PublicStatus
from .motion import MotionConfig
from .state import StateStore
from .tic import SubprocessTicBackend


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="platectl",
        description="Safely operate the two-position random-dot glass lift.",
    )
    parser.add_argument("command", choices=["up", "down", "home", "shutdown", "status"])
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--serial", help="Tic USB serial number when more than one is connected")
    parser.add_argument("--ticcmd", default="ticcmd", help="path to Pololu ticcmd")
    parser.add_argument(
        "--backend",
        choices=["ticcmd", "mock"],
        default="ticcmd",
        help="mock is only for software tests and never proves hardware safety",
    )
    parser.add_argument("--state-dir", type=Path, help="override persistent state directory")
    parser.add_argument(
        "--travel-mm",
        type=int,
        choices=[50, 68],
        default=68,
        help="installed stroke: 68 for R10/R11 (default), 50 for earlier frames",
    )
    return parser


def _format_human(action: str, status: PublicStatus) -> str:
    fault = ", ".join(status.fault) if status.fault else "none"
    return "\n".join(
        [
            f"action: {action}",
            f"backend: {status.backend}",
            f"position: {status.position.value}",
            f"limit: {status.limit.value}",
            f"motor: {'energized' if status.motor_energized else 'de-energized'}",
            f"fault: {fault}",
            f"safe_to_image: {str(status.safe_to_image).lower()}",
            f"safe_to_service: {str(status.safe_to_service).lower()}",
            f"safe_to_unplug: {str(status.safe_to_unplug).lower()}",
        ]
    )


def run(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    motion = MotionConfig(
        travel_mm=args.travel_mm, move_timeout_s=20 if args.travel_mm == 68 else 10
    )
    store = StateStore(args.state_dir, travel_mm=args.travel_mm)
    backend = (
        MockTicBackend(motion=motion)
        if args.backend == "mock"
        else SubprocessTicBackend(executable=args.ticcmd, serial=args.serial)
    )
    controller = PlateController(backend=backend, store=store, motion=motion)

    try:
        store.directory.mkdir(parents=True, exist_ok=True)
        try:
            command_lock = FileLock(store.lock_path, timeout=0)
            command_lock.acquire()
        except Timeout as exc:
            raise ConcurrentCommandError("another platectl process owns the command lock") from exc
        try:
            if args.command == "status":
                result = controller.public_status()
            elif args.command == "home":
                result = controller.move(Endpoint.DOWN, force_home=True)
            elif args.command == "down":
                result = controller.move(Endpoint.DOWN)
            elif args.command == "up":
                result = controller.move(Endpoint.UP)
            else:
                result = controller.shutdown()
        finally:
            command_lock.release()
    except PlateLiftError as exc:
        payload = {"action": args.command, "ok": False, "error": str(exc)}
        if args.as_json:
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(f"platectl: {exc}", file=sys.stderr)
        return exc.exit_code

    payload = {"action": args.command, "ok": True, **result.to_dict()}
    if args.as_json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(_format_human(args.command, result))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
