import pytest
from say_specs import SAY_SPECS, get_pitch_specs


def test_all_pitch_types_present():
    assert set(SAY_SPECS.keys()) == {"7v7", "9v9", "11v11"}


def test_11v11_specs():
    s = get_pitch_specs("11v11")
    assert s["circle_radius"] == 10
    assert s["goal_area_width"] == 20
    assert s["goal_area_depth"] == 6
    assert s["penalty_area_width"] == 44
    assert s["penalty_area_depth"] == 18
    assert s["penalty_mark_dist"] == 12
    assert s["arc_radius"] == 10
    assert s["corner_radius"] == 1
    assert s["build_out_lines"] is False


def test_9v9_specs():
    s = get_pitch_specs("9v9")
    assert s["circle_radius"] == 8
    assert s["goal_area_width"] == 16
    assert s["goal_area_depth"] == 5
    assert s["penalty_area_width"] == 36
    assert s["penalty_area_depth"] == 14
    assert s["penalty_mark_dist"] == 10
    assert s["arc_radius"] == 8
    assert s["corner_radius"] == 1
    assert s["build_out_lines"] is False


def test_7v7_specs():
    s = get_pitch_specs("7v7")
    assert s["circle_radius"] == 8
    assert s["goal_area_width"] == 8
    assert s["goal_area_depth"] == 4
    assert s["penalty_area_width"] == 24
    assert s["penalty_area_depth"] == 12
    assert s["penalty_mark_dist"] == 10
    assert s["arc_radius"] == 8
    assert s["corner_radius"] == 1
    assert s["build_out_lines"] is True


def test_unknown_pitch_type_raises():
    with pytest.raises(KeyError, match="Unknown pitch type"):
        get_pitch_specs("4v4")
