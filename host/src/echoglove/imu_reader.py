from __future__ import annotations

from typing import Iterator

from echoglove.serial_reader import ParseError, stream_port

_QUAT_KEYS = ("w", "x", "y", "z")


def _is_quaternion_msg(d: dict) -> bool:
    return all(k in d for k in _QUAT_KEYS)


def parse_quaternion(d: dict) -> tuple[float, float, float, float]:
    for key in _QUAT_KEYS:
        if key not in d:
            raise ParseError(f"missing key '{key}' in {d!r}")
        if not isinstance(d[key], (int, float)):
            raise ParseError(f"non-numeric value for '{key}' in {d!r}")
    return (float(d["w"]), float(d["x"]), float(d["y"]), float(d["z"]))


def quaternion_stream(port: str, baud: int = 115200) -> Iterator[tuple[float, float, float, float]]:
    for msg in stream_port(port, baud):
        if _is_quaternion_msg(msg):
            yield parse_quaternion(msg)
