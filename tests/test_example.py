import subprocess
import sys
from pathlib import Path


def test_default_capture_example_never_needs_usb() -> None:
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(root / "examples/capture_sequence.py"), "--cycles", "2"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "backend: mock" in result.stdout
    assert result.stdout.count("calibration capture") == 2
    assert result.stdout.count("sample capture") == 2
    assert "finished: DOWN / motor off" in result.stdout
