"""V3 verification: record 5 min of quaternions, assert no discontinuous jumps."""
from __future__ import annotations

import sys
import time

from echoglove.imu_reader import quaternion_stream

_DURATION = 300.0  # 5 minutes
_MIN_DOT = 0.99    # consecutive quaternions must have |dot| >= this


def _dot(q1: tuple, q2: tuple) -> float:
    return sum(a * b for a, b in zip(q1, q2))


def verify_no_jumps(port: str) -> None:
    print(f"Recording {_DURATION:.0f} s of quaternions on {port} ...")
    print("Move the sensor around naturally. Press Ctrl-C to stop early.")
    samples: list[tuple] = []
    start = time.monotonic()
    deadline = start + _DURATION
    try:
        for quat in quaternion_stream(port):
            samples.append(quat)
            elapsed = time.monotonic() - start
            if len(samples) % 1000 == 0:
                print(f"  {elapsed:.0f}s — {len(samples)} samples collected...")
            if time.monotonic() >= deadline:
                break
    except KeyboardInterrupt:
        print()

    print(f"Collected {len(samples)} samples.")
    if len(samples) < 2:
        print("FAIL — not enough samples")
        raise SystemExit(1)

    jumps = []
    for i in range(1, len(samples)):
        d = abs(_dot(samples[i - 1], samples[i]))
        if d < _MIN_DOT:
            jumps.append((i, d))

    if jumps:
        print(f"FAIL — {len(jumps)} jump(s) detected:")
        for idx, d in jumps[:10]:
            print(f"  sample {idx}: |dot| = {d:.5f}  (threshold {_MIN_DOT})")
        raise SystemExit(1)
    else:
        print(f"PASS — all {len(samples) - 1} consecutive pairs have |dot| >= {_MIN_DOT}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: uv run python scripts/verify_no_jumps.py /dev/tty.usbmodemXXXX")
        raise SystemExit(2)
    verify_no_jumps(sys.argv[1])
