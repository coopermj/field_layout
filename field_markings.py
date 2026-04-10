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

    # ── Center circle (polygon) ──────────────────────────────────────────────
    circle_r = specs["circle_radius"] * s
    add_circle_poly(make_circle(0.0, 0.0, circle_r), "center_circle")

    # ── Center mark ─────────────────────────────────────────────────────────
    add_point((0.0, 0.0), "center_mark")

    ga_hw = specs["goal_area_width"] / 2 * s
    ga_d = specs["goal_area_depth"] * s
    pa_hw = specs["penalty_area_width"] / 2 * s
    pa_d = specs["penalty_area_depth"] * s
    pm_d = specs["penalty_mark_dist"] * s
    arc_r = specs["arc_radius"] * s
    cr = specs["corner_radius"] * s

    # ── Both ends (near = negative x, far = positive x) ─────────────────────
    for sign, end_label in [(-1, "near"), (1, "far")]:
        end_x = sign * hl

        # Goal area — 3-sided polyline (goal line closes the 4th side)
        add_line([
            (end_x,              -ga_hw),
            (end_x - sign * ga_d, -ga_hw),
            (end_x - sign * ga_d,  ga_hw),
            (end_x,               ga_hw),
        ], f"goal_area_{end_label}")

        # Penalty area — 3-sided polyline
        add_line([
            (end_x,              -pa_hw),
            (end_x - sign * pa_d, -pa_hw),
            (end_x - sign * pa_d,  pa_hw),
            (end_x,               pa_hw),
        ], f"penalty_area_{end_label}")

        # Penalty mark
        add_point((end_x - sign * pm_d, 0.0), f"penalty_mark_{end_label}")

        # Penalty arc — full circle centered on penalty mark
        pm_local_x = end_x - sign * pm_d
        add_circle_poly(make_circle(pm_local_x, 0.0, arc_r), f"penalty_arc_{end_label}")

        # Penalty arc mask — rectangle occluding the arc inside the penalty area
        # Spans from goal line to penalty area back edge, tall enough to cover circle
        mask_x0 = end_x
        mask_x1 = end_x - sign * pa_d
        pa_mask_buf = arc_r + 2 * s
        add_mask(
            make_closed_rect(
                min(mask_x0, mask_x1), max(mask_x0, mask_x1),
                -pa_mask_buf, pa_mask_buf,
            ),
            f"penalty_arc_mask_{end_label}",
        )

        # Corner arcs — full circle at each corner + 2 occlusion masks each
        corner_buf = cr + 2 * s  # padding beyond circle

        for side, side_label in [(-1, "left"), (1, "right")]:
            corner_x = end_x
            corner_y = side * hw

            add_circle_poly(
                make_circle(corner_x, corner_y, cr),
                f"corner_arc_{end_label}_{side_label}",
            )

            # Mask 1: outside the goal line (away from field in x direction)
            goal_mask_x_outer = corner_x + sign * corner_buf
            add_mask(
                make_closed_rect(
                    min(goal_mask_x_outer, corner_x),
                    max(goal_mask_x_outer, corner_x),
                    corner_y - corner_buf,
                    corner_y + corner_buf,
                ),
                f"corner_arc_mask_{end_label}_{side_label}_goal",
            )

            # Mask 2: outside the touchline (away from field in y direction)
            touch_mask_y_outer = corner_y + side * corner_buf
            add_mask(
                make_closed_rect(
                    corner_x - corner_buf,
                    corner_x + corner_buf,
                    min(touch_mask_y_outer, corner_y),
                    max(touch_mask_y_outer, corner_y),
                ),
                f"corner_arc_mask_{end_label}_{side_label}_touchline",
            )

    # ── Build-out lines (7v7 only) ───────────────────────────────────────────
    if specs["build_out_lines"]:
        for sign, end_label in [(-1, "near"), (1, "far")]:
            # pa_back_x: sign*(hl - pa_d) = for near: -(hl - pa_d) = -hl + pa_d
            pa_back_x = sign * (hl - pa_d)
            bo_x = pa_back_x / 2  # midpoint between pa_back_x and 0 (halfway line)
            add_line([(bo_x, -hw), (bo_x, hw)], f"build_out_line_{end_label}")

    return {"lines": lines, "circles": circles, "masks": masks, "points": points}
