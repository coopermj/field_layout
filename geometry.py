import math
import numpy as np


def rotate_translate(pts, angle_rad, origin):
    """
    Rotate pts (local coords) by angle_rad CCW around (0,0), then translate to origin.

    Args:
        pts: list of (x, y) tuples in local coordinates
        angle_rad: rotation angle in radians (CCW positive)
        origin: (ox, oy) world coordinates of the local origin

    Returns:
        list of (float, float) tuples in world coordinates
    """
    ox, oy = origin
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return [
        (ox + x * cos_a - y * sin_a, oy + x * sin_a + y * cos_a)
        for x, y in pts
    ]
