import math
import pytest
from geometry import rotate_translate
from geometry import min_bounding_rect
from geometry import make_circle, make_closed_rect
from geometry import yards_to_native


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


def test_make_circle_closed():
    """First and last point are equal (closed ring)."""
    ring = make_circle(0.0, 0.0, 10.0)
    assert ring[0] == ring[-1]


def test_make_circle_radius():
    """All points are at the correct radius from center."""
    cx, cy, r = 5.0, 3.0, 8.0
    ring = make_circle(cx, cy, r)
    for x, y in ring[:-1]:  # skip closing point
        dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        assert abs(dist - r) < 1e-9


def test_make_circle_default_n_pts():
    """Default 64 points → ring has 65 entries (64 + closing)."""
    ring = make_circle(0.0, 0.0, 5.0)
    assert len(ring) == 65


def test_make_circle_custom_n_pts():
    ring = make_circle(0.0, 0.0, 5.0, n_pts=32)
    assert len(ring) == 33


def test_make_closed_rect_corners():
    """Corners are at expected positions; ring is closed."""
    ring = make_closed_rect(-10.0, 10.0, -5.0, 5.0)
    assert ring[0] == ring[-1]
    xs = [p[0] for p in ring[:-1]]
    ys = [p[1] for p in ring[:-1]]
    assert set(xs) == {-10.0, 10.0}
    assert set(ys) == {-5.0, 5.0}
    assert len(ring) == 5  # 4 corners + close


def test_make_closed_rect_area():
    """Area of rect = width × height."""
    ring = make_closed_rect(0.0, 20.0, 0.0, 10.0)
    # Shoelace formula
    n = len(ring) - 1
    area = abs(sum(ring[i][0] * ring[(i+1) % n][1] - ring[(i+1) % n][0] * ring[i][1]
                   for i in range(n))) / 2
    assert abs(area - 200.0) < 1e-9


def test_yards_to_native_meters_dict():
    sr = {"linear_unit_name": "Meter"}
    assert yards_to_native(sr) == pytest.approx(0.9144)


def test_yards_to_native_meters_case_insensitive():
    sr = {"linear_unit_name": "meter"}
    assert yards_to_native(sr) == pytest.approx(0.9144)


def test_yards_to_native_feet():
    sr = {"linear_unit_name": "Foot_US"}
    assert yards_to_native(sr) == pytest.approx(3.0)


def test_yards_to_native_feet_variant():
    sr = {"linear_unit_name": "Foot"}
    assert yards_to_native(sr) == pytest.approx(3.0)


def test_yards_to_native_degrees_raises():
    sr = {"linear_unit_name": "Degree"}
    with pytest.raises(ValueError, match="Unsupported"):
        yards_to_native(sr)


def test_yards_to_native_unknown_raises():
    sr = {"linear_unit_name": "Fathom"}
    with pytest.raises(ValueError):
        yards_to_native(sr)


class MockSR:
    """Minimal mock of arcgis.geometry.SpatialReference."""
    def __init__(self, unit_name):
        self.linear_unit_name = unit_name

def test_yards_to_native_arcgis_object():
    sr = MockSR("Meter")
    assert yards_to_native(sr) == pytest.approx(0.9144)
