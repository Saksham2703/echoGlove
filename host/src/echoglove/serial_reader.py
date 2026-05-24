from __future__ import annotations

import json
from typing import BinaryIO, Iterator


class ParseError(ValueError):
    """Raised when a non-blank line is not valid JSON."""


def parse_lines(stream: BinaryIO) -> Iterator[dict]:
    """Yield one parsed dict per newline-terminated JSON line in stream.

    A trailing line without a newline is treated as incomplete and dropped.
    Blank lines are skipped silently.
    """
    buf = b""
    while True:
        chunk = stream.read(1024)
        if not chunk:
            break
        buf += chunk

    *lines, _tail = buf.split(b"\n")

    for raw in lines:
        line = raw.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError as e:
            raise ParseError(f"could not parse line: {line!r}") from e


def stream_port(port: str, baud: int = 115200) -> Iterator[dict]:
    """Open a real serial port and yield parsed dicts forever.

    Reads line-by-line so output appears as it arrives.
    Not unit-tested (needs hardware). Use parse_lines() for anything testable.
    """
    import serial  # lazy import so tests don't need hardware

    with serial.Serial(port, baud, timeout=1) as ser:
        while True:
            raw = ser.readline()
            if not raw:
                continue
            line = raw.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                raise ParseError(f"could not parse line: {line!r}") from e


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("usage: python -m echoglove.serial_reader /dev/tty.usbmodemXXXX")
        raise SystemExit(2)
    for msg in stream_port(sys.argv[1]):
        print(msg)
