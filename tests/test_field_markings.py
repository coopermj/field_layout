import math
import pytest
from field_markings import build_field_markings

# 110×70 yd axis-aligned field centered at origin; scale=1.0 (units are yards)
FIELD_110x70 = [(-55.0, -35.0), (55.0, -35.0), (55.0, 35.0), (-55.0, 35.0), (-55.0, -35.0)]


def _lines_by_type(result):
    out = {}
    for f in result["lines"]:
        ct = f["attributes"]["component_type"]
        out.setdefault(ct, []).append(f)
    return out


def _pts_by_type(result):
    out = {}
    for f in result["points"]:
        ct = f["attributes"]["component_type"]
        out.setdefault(ct, []).append(f)
    return out


def test_boundary_lines_count_11v11():
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    by_type = _lines_by_type(result)
    assert len(by_type["touchline"]) == 2
    assert len(by_type["goal_line"]) == 2
    assert len(by_type["halfway_line"]) == 1


def test_touchlines_span_full_length():
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    by_type = _lines_by_type(result)
    for feat in by_type["touchline"]:
        path = feat["geometry"]["paths"][0]
        xs = [p[0] for p in path]
        assert abs(min(xs) - (-55.0)) < 0.1
        assert abs(max(xs) - 55.0) < 0.1


def test_halfway_line_at_center():
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    by_type = _lines_by_type(result)
    path = by_type["halfway_line"][0]["geometry"]["paths"][0]
    xs = [p[0] for p in path]
    assert all(abs(x) < 0.1 for x in xs)  # all x ≈ 0


def test_field_id_on_all_features():
    result = build_field_markings(FIELD_110x70, "11v11", field_id=42, scale=1.0)
    all_features = (result["lines"] + result["circles"] +
                    result["masks"] + result["points"])
    for f in all_features:
        assert f["attributes"]["field_id"] == 42


def test_pitch_type_on_all_features():
    result = build_field_markings(FIELD_110x70, "9v9", field_id=1, scale=1.0)
    all_features = (result["lines"] + result["circles"] +
                    result["masks"] + result["points"])
    for f in all_features:
        assert f["attributes"]["pitch_type"] == "9v9"


def test_unknown_pitch_type_raises():
    with pytest.raises(KeyError):
        build_field_markings(FIELD_110x70, "6v6", field_id=1, scale=1.0)


def test_penalty_area_count():
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    by_type = _lines_by_type(result)
    assert len(by_type["penalty_area_near"]) == 1
    assert len(by_type["penalty_area_far"]) == 1


def test_goal_area_count():
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    by_type = _lines_by_type(result)
    assert len(by_type["goal_area_near"]) == 1
    assert len(by_type["goal_area_far"]) == 1


def test_11v11_penalty_area_dimensions():
    """11v11 penalty area: 44 yds wide (±22 from center), 18 yds deep."""
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    by_type = _lines_by_type(result)
    pa_near = by_type["penalty_area_near"][0]
    path = pa_near["geometry"]["paths"][0]
    ys = [p[1] for p in path]
    xs = [p[0] for p in path]
    assert abs(min(ys) - (-22.0)) < 0.1   # half of 44
    assert abs(max(ys) - 22.0) < 0.1
    # Back edge: -55 + 18 = -37
    assert abs(max(xs) - (-37.0)) < 0.1


def test_11v11_goal_area_dimensions():
    """11v11 goal area: 20 yds wide (±10 from center), 6 yds deep."""
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    by_type = _lines_by_type(result)
    ga_near = by_type["goal_area_near"][0]
    path = ga_near["geometry"]["paths"][0]
    ys = [p[1] for p in path]
    xs = [p[0] for p in path]
    assert abs(min(ys) - (-10.0)) < 0.1
    assert abs(max(ys) - 10.0) < 0.1
    # Back edge: -55 + 6 = -49
    assert abs(max(xs) - (-49.0)) < 0.1


def test_scale_applied_to_areas():
    """With scale=0.9144 (meters), penalty area width should be 44*0.9144 m wide."""
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=0.9144)
    by_type = _lines_by_type(result)
    pa_near = by_type["penalty_area_near"][0]
    path = pa_near["geometry"]["paths"][0]
    ys = [p[1] for p in path]
    expected_half = 22 * 0.9144
    assert abs(min(ys) - (-expected_half)) < 0.01
    assert abs(max(ys) - expected_half) < 0.01


def test_center_circle_in_circles_layer():
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    circle_types = [f["attributes"]["component_type"] for f in result["circles"]]
    assert "center_circle" in circle_types


def test_11v11_center_circle_radius():
    """11v11 center circle radius = 10 yds; verify a point on the ring."""
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    cc = next(f for f in result["circles"]
              if f["attributes"]["component_type"] == "center_circle")
    ring = cc["geometry"]["rings"][0]
    # Check radius of each vertex
    for x, y in ring[:-1]:
        r = math.sqrt(x ** 2 + y ** 2)
        assert abs(r - 10.0) < 0.01


def test_center_mark_at_origin():
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    cm = next(f for f in result["points"]
              if f["attributes"]["component_type"] == "center_mark")
    assert abs(cm["geometry"]["x"]) < 0.01
    assert abs(cm["geometry"]["y"]) < 0.01


def test_11v11_penalty_marks_position():
    """11v11 penalty marks: 12 yds from goal line. Near: x = -55+12 = -43."""
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    by_type = _pts_by_type(result)
    near = by_type["penalty_mark_near"][0]
    far = by_type["penalty_mark_far"][0]
    assert abs(near["geometry"]["x"] - (-43.0)) < 0.1
    assert abs(near["geometry"]["y"]) < 0.1
    assert abs(far["geometry"]["x"] - 43.0) < 0.1


def test_9v9_penalty_marks_position():
    """9v9 penalty marks: 10 yds from goal line. On 110×70 field: x = ±45."""
    result = build_field_markings(FIELD_110x70, "9v9", field_id=1, scale=1.0)
    by_type = _pts_by_type(result)
    assert abs(by_type["penalty_mark_near"][0]["geometry"]["x"] - (-45.0)) < 0.1
    assert abs(by_type["penalty_mark_far"][0]["geometry"]["x"] - 45.0) < 0.1


def test_penalty_arc_circles_present():
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    circle_types = [f["attributes"]["component_type"] for f in result["circles"]]
    assert "penalty_arc_near" in circle_types
    assert "penalty_arc_far" in circle_types


def test_11v11_penalty_arc_radius():
    """11v11 arc radius = 10 yds, centered on penalty mark at (-43, 0)."""
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    arc = next(f for f in result["circles"]
               if f["attributes"]["component_type"] == "penalty_arc_near")
    ring = arc["geometry"]["rings"][0]
    pm_x = -55.0 + 12.0  # -43
    for x, y in ring[:-1]:
        r = math.sqrt((x - pm_x) ** 2 + y ** 2)
        assert abs(r - 10.0) < 0.01


def test_penalty_arc_masks_present():
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    mask_types = [f["attributes"]["component_type"] for f in result["masks"]]
    assert "penalty_arc_mask_near" in mask_types
    assert "penalty_arc_mask_far" in mask_types


def test_penalty_arc_mask_covers_penalty_area_depth():
    """Near mask x range should span from goal line to penalty area back edge."""
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    mask = next(f for f in result["masks"]
                if f["attributes"]["component_type"] == "penalty_arc_mask_near")
    ring = mask["geometry"]["rings"][0]
    xs = [p[0] for p in ring]
    # Should span from ≈-55 (goal line) to ≈-37 (penalty area back edge = -55+18)
    assert min(xs) <= -55.0 + 0.1
    assert max(xs) >= -37.0 - 0.1


def test_corner_arc_circles_count():
    """4 corner arcs total (near+far × left+right)."""
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    corner_circles = [f for f in result["circles"]
                      if "corner_arc" in f["attributes"]["component_type"]
                      and "mask" not in f["attributes"]["component_type"]]
    assert len(corner_circles) == 4


def test_corner_arc_radius():
    """Corner arc radius = 1 yd; circle centered at field corner."""
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    arc = next(f for f in result["circles"]
               if f["attributes"]["component_type"] == "corner_arc_near_left")
    ring = arc["geometry"]["rings"][0]
    # Corner at (-55, -35)
    for x, y in ring[:-1]:
        r = math.sqrt((x - (-55.0)) ** 2 + (y - (-35.0)) ** 2)
        assert abs(r - 1.0) < 0.01


def test_corner_arc_masks_count():
    """8 masks total: 2 per corner × 4 corners."""
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    corner_masks = [f for f in result["masks"]
                    if "corner" in f["attributes"]["component_type"]]
    assert len(corner_masks) == 8


def test_corner_arc_mask_goal_side_covers_outside():
    """Goal-side mask for near-left corner should cover x < -55."""
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    mask = next(f for f in result["masks"]
                if f["attributes"]["component_type"] == "corner_arc_mask_near_left_goal")
    ring = mask["geometry"]["rings"][0]
    xs = [p[0] for p in ring]
    assert min(xs) < -55.0  # extends beyond goal line


def test_corner_arc_mask_touchline_side_covers_outside():
    """Touchline-side mask for near-left corner should cover y < -35."""
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    mask = next(f for f in result["masks"]
                if f["attributes"]["component_type"] == "corner_arc_mask_near_left_touchline")
    ring = mask["geometry"]["rings"][0]
    ys = [p[1] for p in ring]
    assert min(ys) < -35.0  # extends beyond touchline
