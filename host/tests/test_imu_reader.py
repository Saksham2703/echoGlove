from __future__ import annotations

import pytest

from echoglove.imu_reader import parse_quaternion, _is_quaternion_msg
from echoglove.serial_reader import ParseError


def test_parse_quaternion_valid():
    result = parse_quaternion({"t_ms": 100, "w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0})
    assert result == (1.0, 0.0, 0.0, 0.0)


def test_parse_quaternion_integer_values():
    result = parse_quaternion({"w": 1, "x": 0, "y": 0, "z": 0})
    assert result == (1.0, 0.0, 0.0, 0.0)
    assert all(isinstance(v, float) for v in result)


def test_parse_quaternion_missing_key():
    with pytest.raises(ParseError, match="missing key"):
        parse_quaternion({"w": 1.0, "x": 0.0, "y": 0.0})  # no "z"


def test_parse_quaternion_non_numeric_value():
    with pytest.raises(ParseError, match="non-numeric"):
        parse_quaternion({"w": "bad", "x": 0.0, "y": 0.0, "z": 0.0})


def test_parse_quaternion_extra_keys_ignored():
    result = parse_quaternion(
        {"t_ms": 999, "w": 0.5, "x": 0.5, "y": 0.5, "z": 0.5, "cal_sys": 3}
    )
    assert result == (0.5, 0.5, 0.5, 0.5)


def test_is_quaternion_msg_true():
    assert _is_quaternion_msg({"w": 1.0, "x": 0.0, "y": 0.0, "z": 0.0}) is True


def test_is_quaternion_msg_false_event():
    assert _is_quaternion_msg({"event": "boot", "phase": 1}) is False


def test_is_quaternion_msg_false_partial():
    assert _is_quaternion_msg({"t_ms": 100, "w": 1.0, "x": 0.0}) is False
