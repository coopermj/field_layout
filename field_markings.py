import math
from geometry import rotate_translate, min_bounding_rect, make_circle, make_closed_rect
from say_specs import get_pitch_specs


def build_field_markings(coords, pitch_type, field_id, scale):
    """
    Generate all field marking features for one field polygon.

    Args:
        coords: list of (x, y) tuples — exterior ring in world coordinates
        pitch_type: "7v7", "9v9", or "11v11"
        field_id: OBJECTID of the source field polygon (for idempotent deletes)
        scale: yards_to_native conversion factor (native units per yard)

    Returns:
        dict with keys 'lines', 'circles', 'masks', 'points'. Each value is a
        list of feature dicts:
          lines:   {"geometry": {"paths": [[[x,y],...]]}, "attributes": {...}}
          circles: {"geometry": {"rings": [[[x,y],...,[x,y]]]}, "attributes": {...}}
          masks:   {"geometry": {"rings": [[[x,y],...,[x,y]]]}, "attributes": {...}}
          points:  {"geometry": {"x": float, "y": float}, "attributes": {...}}
    """
    specs = get_pitch_specs(pitch_type)
    cx, cy, length, width, angle = min_bounding_rect(coords)

    hl = length / 2  # half-length (touchline direction)
    hw = width / 2   # half-width (goal line direction)
    s = scale

    lines, circles, masks, points = [], [], [], []

    def attrs(component_type):
        return {"field_id": field_id, "component_type": component_type,
                "pitch_type": pitch_type}

    def add_line(local_pts, component_type):
        world = rotate_translate(local_pts, angle, (cx, cy))
        lines.append({
            "geometry": {"paths": [[[x, y] for x, y in world]]},
            "attributes": attrs(component_type),
        })

    def add_circle_poly(local_ring, component_type):
        world = rotate_translate(local_ring, angle, (cx, cy))
        circles.append({
            "geometry": {"rings": [[[x, y] for x, y in world]]},
            "attributes": attrs(component_type),
        })

    def add_mask(local_ring, component_type):
        world = rotate_translate(local_ring, angle, (cx, cy))
        masks.append({
            "geometry": {"rings": [[[x, y] for x, y in world]]},
            "attributes": attrs(component_type),
        })

    def add_point(local_pt, component_type):
        wx, wy = rotate_translate([local_pt], angle, (cx, cy))[0]
        points.append({
            "geometry": {"x": wx, "y": wy},
            "attributes": attrs(component_type),
        })

    # ── Boundary lines ──────────────────────────────────────────────────────
    add_line([(-hl, -hw), (hl, -hw)], "touchline")
    add_line([(-hl,  hw), (hl,  hw)], "touchline")
    add_line([(-hl, -hw), (-hl, hw)], "goal_line")
    add_line([( hl, -hw), ( hl, hw)], "goal_line")
    add_line([(0,   -hw), (0,   hw)], "halfway_line")

    # ── Both ends (near = negative x, far = positive x) ─────────────────────
    for sign, end_label in [(-1, "near"), (1, "far")]:
        end_x = sign * hl

        # Goal area — 3-sided polyline (goal line closes the 4th side)
        ga_hw = specs["goal_area_width"] / 2 * s
        ga_d = specs["goal_area_depth"] * s
        add_line([
            (end_x,              -ga_hw),
            (end_x - sign * ga_d, -ga_hw),
            (end_x - sign * ga_d,  ga_hw),
            (end_x,               ga_hw),
        ], f"goal_area_{end_label}")

        # Penalty area — 3-sided polyline
        pa_hw = specs["penalty_area_width"] / 2 * s
        pa_d = specs["penalty_area_depth"] * s
        add_line([
            (end_x,              -pa_hw),
            (end_x - sign * pa_d, -pa_hw),
            (end_x - sign * pa_d,  pa_hw),
            (end_x,               pa_hw),
        ], f"penalty_area_{end_label}")

    return {"lines": lines, "circles": circles, "masks": masks, "points": points}
