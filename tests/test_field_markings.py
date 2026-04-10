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
