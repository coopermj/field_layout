SAY_SPECS = {
    "11v11": {
        "circle_radius": 10,
        "corner_radius": 1,
        "goal_area_width": 20,
        "goal_area_depth": 6,
        "penalty_area_width": 44,
        "penalty_area_depth": 18,
        "penalty_mark_dist": 12,
        "arc_radius": 10,
        "build_out_lines": False,
    },
    "9v9": {
        "circle_radius": 8,
        "corner_radius": 1,
        "goal_area_width": 16,
        "goal_area_depth": 5,
        "penalty_area_width": 36,
        "penalty_area_depth": 14,
        "penalty_mark_dist": 10,
        "arc_radius": 8,
        "build_out_lines": False,
    },
    "7v7": {
        "circle_radius": 8,
        "corner_radius": 1,
        "goal_area_width": 8,
        "goal_area_depth": 4,
        "penalty_area_width": 24,
        "penalty_area_depth": 12,
        "penalty_mark_dist": 10,
        "arc_radius": 8,
        "build_out_lines": True,
    },
}


def get_pitch_specs(pitch_type):
    """Return SAY spec dict for pitch_type. Raises KeyError for unknown types."""
    if pitch_type not in SAY_SPECS:
        raise KeyError(
            f"Unknown pitch type: {pitch_type!r}. Must be one of {sorted(SAY_SPECS)}"
        )
    return dict(SAY_SPECS[pitch_type])
