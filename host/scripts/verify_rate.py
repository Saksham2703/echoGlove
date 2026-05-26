"""V1 verification: measure quaternion stream rate over 10 s. Pass if >= 95 Hz."""
from __future__ import annotations

import sys
import time

from echoglove.serial_reader import stream_port

_QUAT_KEYS = ("w", "x", "y", "z")
_DURATION = 10.0
_MIN_HZ = 95.0


def verify_rate(port: str) -> None:
    print(f"Counting quaternion lines for {_DURATION:.0f} s on {port} ...")
    count = 0
    start = time.monotonic()
    deadline = start + _DURATION
    for msg in stream_port(port):
        if all(k in msg for k in _QUAT_KEYS):
            count += 1
        if time.monotonic() >= deadline:
            break
    elapsed = time.monotonic() - start
    hz = count / elapsed
    print(f"Measured: {hz:.1f} Hz ({count} samples in {elapsed:.2f} s)")
    if hz >= _MIN_HZ:
        print("PASS")
    else:
        print(f"FAIL — expected >= {_MIN_HZ} Hz")
        raise SystemExit(1)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: uv run python scripts/verify_rate.py /dev/tty.usbmodemXXXX")
        raise SystemExit(2)
    verify_rate(sys.argv[1])
