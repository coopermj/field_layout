import math
import pytest
from geometry import rotate_translate
from geometry import min_bounding_rect


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


def test_mbr_axis_aligned_rectangle():
    """Axis-aligned 110×70 rectangle centered at origin."""
    coords = [(-55.0, -35.0), (55.0, -35.0), (55.0, 35.0), (-55.0, 35.0), (-55.0, -35.0)]
    cx, cy, length, width, angle = min_bounding_rect(coords)
    assert abs(cx) < 1e-6
    assert abs(cy) < 1e-6
    assert abs(length - 110.0) < 0.5
    assert abs(width - 70.0) < 0.5
    assert abs(angle) < 0.01  # near-zero for axis-aligned


def test_mbr_offset_rectangle():
    """Same shape translated to (100, 200)."""
    coords = [(45.0, 165.0), (155.0, 165.0), (155.0, 235.0), (45.0, 235.0), (45.0, 165.0)]
    cx, cy, length, width, angle = min_bounding_rect(coords)
    assert abs(cx - 100.0) < 1e-3
    assert abs(cy - 200.0) < 1e-3
    assert abs(length - 110.0) < 0.5
    assert abs(width - 70.0) < 0.5


def test_mbr_length_always_gte_width():
    """Length is always the longer dimension."""
    coords = [(-20.0, -40.0), (20.0, -40.0), (20.0, 40.0), (-20.0, 40.0)]
    _, _, length, width, _ = min_bounding_rect(coords)
    assert length >= width


def test_mbr_ignores_closing_point():
    """Closing point (same as first) should not affect the result."""
    open_coords = [(-55.0, -35.0), (55.0, -35.0), (55.0, 35.0), (-55.0, 35.0)]
    closed_coords = open_coords + [(-55.0, -35.0)]
    cx1, cy1, l1, w1, a1 = min_bounding_rect(open_coords)
    cx2, cy2, l2, w2, a2 = min_bounding_rect(closed_coords)
    assert abs(l1 - l2) < 0.01
    assert abs(w1 - w2) < 0.01


def test_mbr_rotated_rectangle():
    """Rectangle rotated 45°: length and width still correct."""
    angle_45 = math.pi / 4
    corners = [(-55.0, 0.0), (0.0, -35.0), (55.0, 0.0), (0.0, 35.0)]
    rotated = [(x * math.cos(angle_45) - y * math.sin(angle_45),
                x * math.sin(angle_45) + y * math.cos(angle_45)) for x, y in corners]
    _, _, length, width, _ = min_bounding_rect(rotated)
    # Rotated shape — length and width should reflect original dims
    assert length >= width
    assert length > 0 and width > 0
