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


def min_bounding_rect(coords):
    """
    Find the minimum bounding rectangle of a polygon using PCA.

    Args:
        coords: list of (x, y) tuples — exterior ring (closing point ignored if duplicate)

    Returns:
        (cx, cy, length, width, angle_rad)
        - (cx, cy): centroid of the MBR
        - length: longer dimension
        - width: shorter dimension
        - angle_rad: orientation of the long axis, normalized to [-π/2, π/2]
    """
    pts = np.array(coords, dtype=float)
    if len(pts) > 1 and np.allclose(pts[0], pts[-1]):
        pts = pts[:-1]

    center = pts.mean(axis=0)
    centered = pts - center
    cov = np.cov(centered.T)
    eigenvalues, eigenvectors = np.linalg.eigh(cov)
    long_idx = int(np.argmax(eigenvalues))
    long_axis = eigenvectors[:, long_idx]
    angle = math.atan2(float(long_axis[1]), float(long_axis[0]))

    cos_a = math.cos(-angle)
    sin_a = math.sin(-angle)
    rot = np.array([[cos_a, -sin_a], [sin_a, cos_a]])
    rotated = (centered @ rot.T)

    d0 = float(rotated[:, 0].max() - rotated[:, 0].min())
    d1 = float(rotated[:, 1].max() - rotated[:, 1].min())

    if d0 >= d1:
        length, width = d0, d1
    else:
        length, width = d1, d0
        angle += math.pi / 2

    # Normalize to [-π/2, π/2]
    while angle > math.pi / 2:
        angle -= math.pi
    while angle < -math.pi / 2:
        angle += math.pi

    return float(center[0]), float(center[1]), length, width, angle
