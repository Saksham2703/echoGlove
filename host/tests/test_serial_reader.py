import io

import pytest

from echoglove.serial_reader import parse_lines, ParseError


def test_parse_valid_json_lines():
    """Lines of well-formed JSON should be yielded as dicts in order."""
    raw = b'{"t_ms": 100, "button_count": 0}\n{"t_ms": 200, "button_count": 1}\n'
    stream = io.BytesIO(raw)
    result = list(parse_lines(stream))
    assert result == [
        {"t_ms": 100, "button_count": 0},
        {"t_ms": 200, "button_count": 1},
    ]


def test_partial_final_line_is_dropped():
    """A trailing line without a newline is incomplete and skipped."""
    raw = b'{"t_ms": 100}\n{"t_ms": 200, "incomplete'
    stream = io.BytesIO(raw)
    result = list(parse_lines(stream))
    assert result == [{"t_ms": 100}]


def test_blank_lines_skipped():
    """Empty lines (heartbeat or transient) are silently dropped."""
    raw = b'\n{"t_ms": 100}\n\n\n{"t_ms": 200}\n'
    stream = io.BytesIO(raw)
    result = list(parse_lines(stream))
    assert result == [{"t_ms": 100}, {"t_ms": 200}]


def test_malformed_json_raises_parse_error():
    """A non-blank line that is not valid JSON raises ParseError."""
    raw = b'{"t_ms": 100}\nnot-json\n'
    stream = io.BytesIO(raw)
    with pytest.raises(ParseError) as exc_info:
        list(parse_lines(stream))
    assert "not-json" in str(exc_info.value)
