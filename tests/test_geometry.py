import math
import pytest
from geometry import rotate_translate


def test_rotate_translate_no_rotation():
    """Points at origin with angle=0 should just translate."""
    pts = [(1.0, 0.0), (0.0, 1.0)]
    result = rotate_translate(pts, 0.0, (10.0, 20.0))
    assert abs(result[0][0] - 11.0) < 1e-9
    assert abs(result[0][1] - 20.0) < 1e-9
    assert abs(result[1][0] - 10.0) < 1e-9
    assert abs(result[1][1] - 21.0) < 1e-9


def test_rotate_translate_90_degrees():
    """(1, 0) rotated 90° CCW → (0, 1), then translated."""
    result = rotate_translate([(1.0, 0.0)], math.pi / 2, (0.0, 0.0))
    assert abs(result[0][0] - 0.0) < 1e-9
    assert abs(result[0][1] - 1.0) < 1e-9


def test_rotate_translate_180_degrees():
    """(1, 0) rotated 180° → (-1, 0)."""
    result = rotate_translate([(1.0, 0.0)], math.pi, (0.0, 0.0))
    assert abs(result[0][0] - (-1.0)) < 1e-9
    assert abs(result[0][1] - 0.0) < 1e-9


def test_rotate_translate_with_origin():
    """Rotate around (0,0) then shift to (5, 5)."""
    result = rotate_translate([(1.0, 0.0)], math.pi / 2, (5.0, 5.0))
    assert abs(result[0][0] - 5.0) < 1e-9
    assert abs(result[0][1] - 6.0) < 1e-9


def test_rotate_translate_returns_list_of_tuples():
    result = rotate_translate([(0.0, 0.0)], 0.0, (1.0, 2.0))
    assert isinstance(result, list)
    assert len(result) == 1
    x, y = result[0]
    assert isinstance(x, float)
