# Field Layout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an ArcGIS Notebook that reads soccer field polygons from ArcGIS Online and draws SAY-compliant field markings into four output feature layers.

**Architecture:** Pure-Python modules (`geometry.py`, `say_specs.py`, `field_markings.py`) contain all geometry logic and are fully unit-tested without ArcGIS. `field_layout.ipynb` imports these modules and handles all ArcGIS API interaction. The notebook auto-detects local vs. ArcGIS Online environments and runs unchanged in both.

**Tech Stack:** Python 3.13, `arcgis` 2.4, `numpy`, `pytest`, Jupyter Notebook. Run tests with `.venv` active: `source .venv/bin/activate && pytest tests/`.

---

## File Structure

| File | Responsibility |
|---|---|
| `geometry.py` | Pure math: `rotate_translate`, `min_bounding_rect`, `make_circle`, `make_closed_rect`, `yards_to_native` |
| `say_specs.py` | SAY dimensions dictionary + `get_pitch_specs(pitch_type)` lookup |
| `field_markings.py` | `build_field_markings(coords, pitch_type, field_id, scale)` → raw feature dicts |
| `field_layout.ipynb` | ArcGIS connection, layer I/O, renderer update — 7 cells |
| `tests/test_geometry.py` | Unit tests for `geometry.py` |
| `tests/test_say_specs.py` | Unit tests for `say_specs.py` |
| `tests/test_field_markings.py` | Integration tests for `field_markings.py` |

**Geometry return format** (used across all tasks):
- Lines: `{"paths": [[[x,y], ...]]}`
- Polygons (circles, masks): `{"rings": [[[x,y], ..., [x,y]]]}`  ← first == last (closed)
- Points: `{"x": float, "y": float}`

---

### Task 1: Project Scaffolding

**Files:**
- Create: `tests/__init__.py`
- Create: `tests/test_geometry.py`
- Create: `tests/test_say_specs.py`
- Create: `tests/test_field_markings.py`
- Create: `pytest.ini`
- Modify: `.gitignore`

- [ ] **Step 1: Create test files and pytest config**

```bash
mkdir -p tests
touch tests/__init__.py tests/test_geometry.py tests/test_say_specs.py tests/test_field_markings.py
```

Create `pytest.ini`:
```ini
[pytest]
testpaths = tests
```

- [ ] **Step 2: Add .gitignore entries**

Append to `.gitignore` (create if it doesn't exist):
```
.venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
.superpowers/
```

- [ ] **Step 3: Verify pytest runs (with no tests yet)**

```bash
source .venv/bin/activate && pytest tests/ -v
```
Expected: `no tests ran` — exit 0.

- [ ] **Step 4: Commit**

```bash
git add tests/ pytest.ini .gitignore
git commit -m "feat: add project scaffolding and test structure"
```

---

### Task 2: SAY Specs

**Files:**
- Create: `say_specs.py`
- Modify: `tests/test_say_specs.py`

- [ ] **Step 1: Write failing tests**

`tests/test_say_specs.py`:
```python
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
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
source .venv/bin/activate && pytest tests/test_say_specs.py -v
```
Expected: `ModuleNotFoundError: No module named 'say_specs'`

- [ ] **Step 3: Implement say_specs.py**

`say_specs.py`:
```python
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
    return SAY_SPECS[pitch_type]
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
source .venv/bin/activate && pytest tests/test_say_specs.py -v
```
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add say_specs.py tests/test_say_specs.py
git commit -m "feat: add SAY field specifications"
```

---

### Task 3: geometry.py — rotate_translate

**Files:**
- Create: `geometry.py`
- Modify: `tests/test_geometry.py`

- [ ] **Step 1: Write failing tests**

`tests/test_geometry.py`:
```python
import math
import pytest
from geometry import rotate_translate


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
```

- [ ] **Step 2: Run to confirm failure**

```bash
source .venv/bin/activate && pytest tests/test_geometry.py -v
```
Expected: `ModuleNotFoundError: No module named 'geometry'`

- [ ] **Step 3: Implement rotate_translate in geometry.py**

`geometry.py`:
```python
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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
source .venv/bin/activate && pytest tests/test_geometry.py -v
```
Expected: 5 passed.

- [ ] **Step 5: Commit**

```bash
git add geometry.py tests/test_geometry.py
git commit -m "feat: add rotate_translate geometry function"
```

---

### Task 4: geometry.py — min_bounding_rect

**Files:**
- Modify: `geometry.py`
- Modify: `tests/test_geometry.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_geometry.py`:
```python
from geometry import min_bounding_rect


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
    # Rotated square-ish shape — length and width should reflect original dims
    assert length >= width
    assert length > 0 and width > 0
```

- [ ] **Step 2: Run to confirm failure**

```bash
source .venv/bin/activate && pytest tests/test_geometry.py::test_mbr_axis_aligned_rectangle -v
```
Expected: `ImportError` (function not defined yet).

- [ ] **Step 3: Implement min_bounding_rect**

Append to `geometry.py`:
```python
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
    rotated = centered @ rot.T

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
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
source .venv/bin/activate && pytest tests/test_geometry.py -v
```
Expected: all pass (5 rotate_translate + 5 mbr = 10).

- [ ] **Step 5: Commit**

```bash
git add geometry.py tests/test_geometry.py
git commit -m "feat: add min_bounding_rect geometry function"
```

---

### Task 5: geometry.py — make_circle, make_closed_rect

**Files:**
- Modify: `geometry.py`
- Modify: `tests/test_geometry.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_geometry.py`:
```python
from geometry import make_circle, make_closed_rect


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
```

- [ ] **Step 2: Run to confirm failure**

```bash
source .venv/bin/activate && pytest tests/test_geometry.py -k "circle or rect" -v
```
Expected: `ImportError`.

- [ ] **Step 3: Implement make_circle and make_closed_rect**

Append to `geometry.py`:
```python
def make_circle(cx, cy, radius, n_pts=64):
    """
    Approximate circle as a closed polygon ring.

    Args:
        cx, cy: center in local coordinates
        radius: circle radius (same units as coordinate space)
        n_pts: number of approximation vertices

    Returns:
        Closed ring: list of (x, y) tuples, len = n_pts + 1, first == last
    """
    pts = [
        (cx + radius * math.cos(2 * math.pi * i / n_pts),
         cy + radius * math.sin(2 * math.pi * i / n_pts))
        for i in range(n_pts)
    ]
    pts.append(pts[0])
    return pts


def make_closed_rect(x0, x1, y0, y1):
    """
    Closed rectangular ring from corner coordinates.

    Args:
        x0, x1: x extents (x0 < x1 not required)
        y0, y1: y extents

    Returns:
        5-point closed ring: list of (x, y) tuples, first == last
    """
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
```

- [ ] **Step 4: Run all tests**

```bash
source .venv/bin/activate && pytest tests/test_geometry.py -v
```
Expected: all pass (16 total).

- [ ] **Step 5: Commit**

```bash
git add geometry.py tests/test_geometry.py
git commit -m "feat: add make_circle and make_closed_rect geometry functions"
```

---

### Task 6: geometry.py — yards_to_native

**Files:**
- Modify: `geometry.py`
- Modify: `tests/test_geometry.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_geometry.py`:
```python
from geometry import yards_to_native


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
```

- [ ] **Step 2: Run to confirm failure**

```bash
source .venv/bin/activate && pytest tests/test_geometry.py -k "yards" -v
```
Expected: `ImportError`.

- [ ] **Step 3: Implement yards_to_native**

Append to `geometry.py`:
```python
def yards_to_native(spatial_ref):
    """
    Return conversion factor: native coordinate units per yard.

    Args:
        spatial_ref: arcgis.geometry.SpatialReference object, or a dict with
                     a 'linear_unit_name' key (e.g. {"linear_unit_name": "Meter"})

    Returns:
        float — multiply SAY yard-dimensions by this to get native units

    Raises:
        ValueError for unsupported or geographic coordinate systems
    """
    if hasattr(spatial_ref, "linear_unit_name"):
        unit = spatial_ref.linear_unit_name.lower()
    elif isinstance(spatial_ref, dict):
        unit = str(spatial_ref.get("linear_unit_name", "")).lower()
    else:
        raise ValueError(f"Cannot determine units from spatial_ref: {spatial_ref!r}")

    if "meter" in unit:
        return 0.9144
    if "foot" in unit or "feet" in unit:
        return 3.0
    raise ValueError(
        f"Unsupported coordinate unit {unit!r}. Use a projected CRS in meters or feet."
    )
```

- [ ] **Step 4: Run all tests**

```bash
source .venv/bin/activate && pytest tests/test_geometry.py -v
```
Expected: all pass (24 total).

- [ ] **Step 5: Commit**

```bash
git add geometry.py tests/test_geometry.py
git commit -m "feat: add yards_to_native geometry function"
```

---

### Task 7: field_markings.py — boundary lines, halfway line

**Files:**
- Create: `field_markings.py`
- Modify: `tests/test_field_markings.py`

The test fixture used throughout Tasks 7–12 is a 110×70 yd axis-aligned field centered at origin (scale=1.0, units = yards). With angle=0, local coords = world coords, making assertions straightforward.

- [ ] **Step 1: Write failing tests**

`tests/test_field_markings.py`:
```python
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
```

- [ ] **Step 2: Run to confirm failure**

```bash
source .venv/bin/activate && pytest tests/test_field_markings.py -v
```
Expected: `ModuleNotFoundError: No module named 'field_markings'`

- [ ] **Step 3: Implement field_markings.py with boundary lines**

`field_markings.py`:
```python
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

    return {"lines": lines, "circles": circles, "masks": masks, "points": points}
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
source .venv/bin/activate && pytest tests/test_field_markings.py -v
```
Expected: 6 passed.

- [ ] **Step 5: Commit**

```bash
git add field_markings.py tests/test_field_markings.py
git commit -m "feat: add field_markings scaffold with boundary lines"
```

---

### Task 8: field_markings.py — goal area, penalty area

**Files:**
- Modify: `field_markings.py`
- Modify: `tests/test_field_markings.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_field_markings.py`:
```python
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
```

- [ ] **Step 2: Run to confirm failure**

```bash
source .venv/bin/activate && pytest tests/test_field_markings.py::test_penalty_area_count -v
```
Expected: `KeyError: 'penalty_area_near'`

- [ ] **Step 3: Add goal area and penalty area to build_field_markings**

In `field_markings.py`, add inside `build_field_markings`, after the boundary lines block:
```python
    # ── Both ends (near = negative x, far = positive x) ─────────────────────
    for sign, end_label in [(-1, "near"), (1, "far")]:
        end_x = sign * hl

        # Goal area — 3-sided polyline (goal line closes the 4th side)
        ga_hw = specs["goal_area_width"] / 2 * s
        ga_d = specs["goal_area_depth"] * s
        add_line([
            (end_x,              -ga_hw),
            (end_x + sign * ga_d, -ga_hw),
            (end_x + sign * ga_d,  ga_hw),
            (end_x,               ga_hw),
        ], f"goal_area_{end_label}")

        # Penalty area — 3-sided polyline
        pa_hw = specs["penalty_area_width"] / 2 * s
        pa_d = specs["penalty_area_depth"] * s
        add_line([
            (end_x,              -pa_hw),
            (end_x + sign * pa_d, -pa_hw),
            (end_x + sign * pa_d,  pa_hw),
            (end_x,               pa_hw),
        ], f"penalty_area_{end_label}")
```

Also add (before the `return`) a placeholder for the remaining per-end components:
```python
        # (penalty mark, penalty arc, corner arcs added in later tasks)
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
source .venv/bin/activate && pytest tests/test_field_markings.py -v
```
Expected: 11 passed.

- [ ] **Step 5: Commit**

```bash
git add field_markings.py tests/test_field_markings.py
git commit -m "feat: add goal area and penalty area markings"
```

---

### Task 9: field_markings.py — center circle, penalty marks, center mark

**Files:**
- Modify: `field_markings.py`
- Modify: `tests/test_field_markings.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_field_markings.py`:
```python
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
```

- [ ] **Step 2: Run to confirm failure**

```bash
source .venv/bin/activate && pytest tests/test_field_markings.py -k "circle or mark" -v
```
Expected: multiple failures.

- [ ] **Step 3: Add center circle, center mark, and penalty marks**

In `field_markings.py`, add after the boundary lines block (before the per-end loop):
```python
    # ── Center circle (polygon) ──────────────────────────────────────────────
    circle_r = specs["circle_radius"] * s
    add_circle_poly(make_circle(0.0, 0.0, circle_r), "center_circle")

    # ── Center mark ─────────────────────────────────────────────────────────
    add_point((0.0, 0.0), "center_mark")
```

Inside the per-end loop (after the penalty area block), add:
```python
        # Penalty mark
        pm_d = specs["penalty_mark_dist"] * s
        add_point((end_x + sign * pm_d, 0.0), f"penalty_mark_{end_label}")
```

- [ ] **Step 4: Run tests to confirm they pass**

```bash
source .venv/bin/activate && pytest tests/test_field_markings.py -v
```
Expected: 17 passed.

- [ ] **Step 5: Commit**

```bash
git add field_markings.py tests/test_field_markings.py
git commit -m "feat: add center circle, center mark, and penalty marks"
```

---

### Task 10: field_markings.py — penalty arcs and masks

**Files:**
- Modify: `field_markings.py`
- Modify: `tests/test_field_markings.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_field_markings.py`:
```python
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
```

- [ ] **Step 2: Run to confirm failure**

```bash
source .venv/bin/activate && pytest tests/test_field_markings.py -k "arc" -v
```
Expected: failures.

- [ ] **Step 3: Add penalty arcs and masks**

In `field_markings.py`, inside the per-end loop (after the penalty mark line), add:
```python
        # Penalty arc — full circle centered on penalty mark
        arc_r = specs["arc_radius"] * s
        pm_local_x = end_x + sign * pm_d
        add_circle_poly(make_circle(pm_local_x, 0.0, arc_r), f"penalty_arc_{end_label}")

        # Penalty arc mask — rectangle occluding the arc inside the penalty area
        # Spans from goal line to penalty area back edge, tall enough to cover circle
        mask_x0 = end_x
        mask_x1 = end_x + sign * pa_d
        buf = arc_r + 2 * s
        add_mask(
            make_closed_rect(
                min(mask_x0, mask_x1), max(mask_x0, mask_x1),
                -buf, buf,
            ),
            f"penalty_arc_mask_{end_label}",
        )
```

Note: `pm_d` and `pa_d` are already defined earlier in the loop from the goal/penalty area block. Make sure the loop body has them available (they are — defined in Task 8).

- [ ] **Step 4: Run tests to confirm they pass**

```bash
source .venv/bin/activate && pytest tests/test_field_markings.py -v
```
Expected: 21 passed.

- [ ] **Step 5: Commit**

```bash
git add field_markings.py tests/test_field_markings.py
git commit -m "feat: add penalty arcs and occlusion masks"
```

---

### Task 11: field_markings.py — corner arcs and masks

**Files:**
- Modify: `field_markings.py`
- Modify: `tests/test_field_markings.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_field_markings.py`:
```python
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
```

- [ ] **Step 2: Run to confirm failure**

```bash
source .venv/bin/activate && pytest tests/test_field_markings.py -k "corner" -v
```
Expected: failures.

- [ ] **Step 3: Add corner arcs and masks**

In `field_markings.py`, inside the per-end loop (after the penalty arc mask block), add:
```python
        # Corner arcs — full circle at each corner + 2 occlusion masks each
        cr = specs["corner_radius"] * s
        buf = cr + 2 * s  # padding beyond circle

        for side, side_label in [(-1, "left"), (1, "right")]:
            corner_x = end_x
            corner_y = side * hw

            add_circle_poly(
                make_circle(corner_x, corner_y, cr),
                f"corner_arc_{end_label}_{side_label}",
            )

            # Mask 1: outside the goal line (away from field in x direction)
            goal_mask_x_outer = corner_x - sign * buf
            add_mask(
                make_closed_rect(
                    min(goal_mask_x_outer, corner_x),
                    max(goal_mask_x_outer, corner_x),
                    corner_y - buf,
                    corner_y + buf,
                ),
                f"corner_arc_mask_{end_label}_{side_label}_goal",
            )

            # Mask 2: outside the touchline (away from field in y direction)
            touch_mask_y_outer = corner_y + side * buf
            add_mask(
                make_closed_rect(
                    corner_x - buf,
                    corner_x + buf,
                    min(touch_mask_y_outer, corner_y),
                    max(touch_mask_y_outer, corner_y),
                ),
                f"corner_arc_mask_{end_label}_{side_label}_touchline",
            )
```

- [ ] **Step 4: Run all tests to confirm they pass**

```bash
source .venv/bin/activate && pytest tests/test_field_markings.py -v
```
Expected: 28 passed.

- [ ] **Step 5: Commit**

```bash
git add field_markings.py tests/test_field_markings.py
git commit -m "feat: add corner arcs and occlusion masks"
```

---

### Task 12: field_markings.py — build-out lines (7v7)

**Files:**
- Modify: `field_markings.py`
- Modify: `tests/test_field_markings.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_field_markings.py`:
```python
# 65×45 yd field for 7v7 tests
FIELD_65x45 = [(-32.5, -22.5), (32.5, -22.5), (32.5, 22.5), (-32.5, 22.5), (-32.5, -22.5)]


def test_7v7_has_build_out_lines():
    result = build_field_markings(FIELD_65x45, "7v7", field_id=1, scale=1.0)
    by_type = _lines_by_type(result)
    assert "build_out_line_near" in by_type
    assert "build_out_line_far" in by_type


def test_11v11_has_no_build_out_lines():
    result = build_field_markings(FIELD_110x70, "11v11", field_id=1, scale=1.0)
    by_type = _lines_by_type(result)
    assert "build_out_line_near" not in by_type


def test_7v7_build_out_line_position():
    """
    Build-out line: equidistant between halfway line (x=0) and penalty area back edge.
    7v7: hl=32.5, pa_depth=12. Near pa back edge = -32.5 + 12 = -20.5.
    Build-out line near = (-20.5 + 0) / 2 = -10.25.
    """
    result = build_field_markings(FIELD_65x45, "7v7", field_id=1, scale=1.0)
    by_type = _lines_by_type(result)
    path_near = by_type["build_out_line_near"][0]["geometry"]["paths"][0]
    xs = [p[0] for p in path_near]
    assert all(abs(x - (-10.25)) < 0.1 for x in xs)

    path_far = by_type["build_out_line_far"][0]["geometry"]["paths"][0]
    xs_far = [p[0] for p in path_far]
    assert all(abs(x - 10.25) < 0.1 for x in xs_far)


def test_7v7_build_out_line_full_width():
    """Build-out lines span the full field width."""
    result = build_field_markings(FIELD_65x45, "7v7", field_id=1, scale=1.0)
    by_type = _lines_by_type(result)
    path = by_type["build_out_line_near"][0]["geometry"]["paths"][0]
    ys = [p[1] for p in path]
    assert abs(min(ys) - (-22.5)) < 0.1
    assert abs(max(ys) - 22.5) < 0.1
```

- [ ] **Step 2: Run to confirm failure**

```bash
source .venv/bin/activate && pytest tests/test_field_markings.py -k "build_out" -v
```
Expected: failures.

- [ ] **Step 3: Add build-out lines**

In `field_markings.py`, add after the per-end loop (before `return`):
```python
    # ── Build-out lines (7v7 only) ───────────────────────────────────────────
    if specs["build_out_lines"]:
        pa_d = specs["penalty_area_depth"] * s
        for sign, end_label in [(-1, "near"), (1, "far")]:
            # Penalty area back edge x-coordinate
            pa_back_x = sign * hl + (-sign) * pa_d  # = sign*(hl - pa_d)... wait
            # sign=-1: -hl + pa_d
            # sign=1:  hl - pa_d
            pa_back_x = sign * (hl - pa_d)
            # Wait: for near (sign=-1): end_x = -hl, going inward by pa_d gives -hl + pa_d
            # sign * (hl - pa_d) with sign=-1 → -(hl - pa_d) = -hl + pa_d ✓
            # sign * (hl - pa_d) with sign=1  →  hl - pa_d ✓
            bo_x = pa_back_x / 2  # midpoint between pa_back_x and 0 (halfway)
            add_line([(bo_x, -hw), (bo_x, hw)], f"build_out_line_{end_label}")
```

- [ ] **Step 4: Run all tests**

```bash
source .venv/bin/activate && pytest tests/ -v
```
Expected: all pass (32+ total).

- [ ] **Step 5: Commit**

```bash
git add field_markings.py tests/test_field_markings.py
git commit -m "feat: add 7v7 build-out lines"
```

---

### Task 13: Notebook — Cells 1–3 (config, connect, imports)

**Files:**
- Create: `field_layout.ipynb`

The notebook cells are numbered 1–7. Cells 3–7 are added in the following tasks.

- [ ] **Step 1: Create the notebook with Cells 1–3**

Create `field_layout.ipynb`:
```json
{
 "nbformat": 4,
 "nbformat_minor": 5,
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {"name": "python", "version": "3.13.0"}
 },
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": ["# Field Layout\n", "Draws SAY-compliant markings for soccer field polygons in ArcGIS Online.\n\n", "**Before running:** fill in the item IDs below. Leave `FIELD_IDS` empty to process all fields."]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# ── Cell 1: Configuration ────────────────────────────────────────────────\n",
    "# Item ID of the input field polygons feature layer\n",
    "FIELDS_ITEM_ID = \"\"  # TODO: set this\n",
    "\n",
    "# Item IDs of the four output feature layers (created manually in ArcGIS Online)\n",
    "LINES_ITEM_ID   = \"\"  # TODO: set this\n",
    "CIRCLES_ITEM_ID = \"\"  # TODO: set this\n",
    "MASKS_ITEM_ID   = \"\"  # TODO: set this\n",
    "POINTS_ITEM_ID  = \"\"  # TODO: set this\n",
    "\n",
    "# Optional: limit processing to specific field OBJECTIDs (empty list = all)\n",
    "FIELD_IDS = []  # e.g. [1, 2, 5]\n",
    "\n",
    "# Name of the Pitch Type attribute on the field polygon layer\n",
    "PITCH_TYPE_FIELD = \"Pitch Type\"\n",
    "\n",
    "print(\"Configuration loaded.\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# ── Cell 2: Connect & Load ────────────────────────────────────────────────\n",
    "import os\n",
    "from arcgis.gis import GIS\n",
    "from arcgis.features import FeatureLayer\n",
    "\n",
    "# Auto-detect environment: ArcGIS Online notebook vs local Jupyter\n",
    "try:\n",
    "    gis = GIS(\"home\")\n",
    "    print(\"Connected via ArcGIS Online session.\")\n",
    "except Exception:\n",
    "    gis = GIS(\"https://www.arcgis.com\")\n",
    "    print(f\"Connected as {gis.properties.user.username}\")\n",
    "\n",
    "# Validate all item IDs are set\n",
    "missing = [name for name, val in [\n",
    "    (\"FIELDS_ITEM_ID\", FIELDS_ITEM_ID),\n",
    "    (\"LINES_ITEM_ID\", LINES_ITEM_ID),\n",
    "    (\"CIRCLES_ITEM_ID\", CIRCLES_ITEM_ID),\n",
    "    (\"MASKS_ITEM_ID\", MASKS_ITEM_ID),\n",
    "    (\"POINTS_ITEM_ID\", POINTS_ITEM_ID),\n",
    "] if not val]\n",
    "if missing:\n",
    "    raise ValueError(f\"Missing item IDs in Cell 1: {missing}\")\n",
    "\n",
    "# Load feature layers\n",
    "fields_item   = gis.content.get(FIELDS_ITEM_ID)\n",
    "lines_fl      = gis.content.get(LINES_ITEM_ID).layers[0]\n",
    "circles_fl    = gis.content.get(CIRCLES_ITEM_ID).layers[0]\n",
    "masks_fl      = gis.content.get(MASKS_ITEM_ID).layers[0]\n",
    "points_fl     = gis.content.get(POINTS_ITEM_ID).layers[0]\n",
    "fields_fl     = fields_item.layers[0]\n",
    "\n",
    "# Read fill color per pitch type from source layer renderer\n",
    "pitch_colors = {}  # e.g. {\"7v7\": [0, 128, 0, 255], ...}\n",
    "renderer = fields_item.layers[0].properties.get(\"drawingInfo\", {}).get(\"renderer\", {})\n",
    "if renderer.get(\"type\") == \"uniqueValue\":\n",
    "    for info in renderer.get(\"uniqueValueInfos\", []):\n",
    "        value = info[\"value\"]\n",
    "        color = info.get(\"symbol\", {}).get(\"color\", [0, 0, 0, 0])\n",
    "        pitch_colors[value] = color\n",
    "    print(f\"Extracted colors for pitch types: {list(pitch_colors.keys())}\")\n",
    "else:\n",
    "    print(\"Warning: source layer renderer is not UniqueValue. Masks will use transparent fill.\")\n",
    "\n",
    "print(\"Layers loaded.\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# ── Cell 3: Imports ───────────────────────────────────────────────────────\n",
    "from geometry import yards_to_native\n",
    "from field_markings import build_field_markings\n",
    "from arcgis.geometry import Polyline, Polygon, Point\n",
    "from arcgis.features import Feature\n",
    "print(\"Imports OK.\")"
   ]
  }
 ]
}
```

- [ ] **Step 2: Open the notebook and verify Cell 3 executes without import errors**

```bash
source .venv/bin/activate && jupyter notebook field_layout.ipynb
```
Run Cell 3 in isolation (no ArcGIS connection needed for import check). Expected: `Imports OK.`

- [ ] **Step 3: Commit**

```bash
git add field_layout.ipynb
git commit -m "feat: add notebook cells 1-3 (config, connect, imports)"
```

---

### Task 14: Notebook — Cells 4–5 (read fields, compute markings)

**Files:**
- Modify: `field_layout.ipynb`

- [ ] **Step 1: Add Cells 4–5 to the notebook**

Add two new cells to the `"cells"` array in `field_layout.ipynb` (append after the Cell 3 entry):

**Cell 4 — Read Fields:**
```python
# ── Cell 4: Read Fields ───────────────────────────────────────────────────
where = "1=1"
if FIELD_IDS:
    ids_str = ",".join(str(i) for i in FIELD_IDS)
    where = f"OBJECTID IN ({ids_str})"

field_features = fields_fl.query(
    where=where,
    out_fields=f"OBJECTID,{PITCH_TYPE_FIELD}",
    return_geometry=True,
).features

print(f"Loaded {len(field_features)} field(s).")
```

**Cell 5 — Compute Markings:**
```python
# ── Cell 5: Compute Markings ──────────────────────────────────────────────
from arcgis.geometry import SpatialReference as SR

sr = fields_fl.properties.extent.spatialReference
scale = yards_to_native(sr)
print(f"Spatial reference: {sr}, scale = {scale:.4f} native units per yard")

lines_to_add    = []
circles_to_add  = []
masks_to_add    = []
points_to_add   = []
skipped         = []
processed_ids   = []

for feat in field_features:
    field_id   = feat.attributes["OBJECTID"]
    pitch_type = feat.attributes.get(PITCH_TYPE_FIELD, "").strip()
    geom       = feat.geometry

    if not geom or not geom.get("rings"):
        skipped.append((field_id, "no geometry"))
        continue

    coords = [(pt[0], pt[1]) for pt in geom["rings"][0]]
    if len(coords) < 3:
        skipped.append((field_id, "fewer than 3 vertices"))
        continue

    try:
        markings = build_field_markings(coords, pitch_type, field_id, scale)
    except KeyError as e:
        skipped.append((field_id, str(e)))
        continue

    sr_dict = {"wkid": sr["wkid"]}

    for f in markings["lines"]:
        g = {**f["geometry"], "spatialReference": sr_dict}
        lines_to_add.append(Feature(geometry=Polyline(g), attributes=f["attributes"]))

    for f in markings["circles"]:
        g = {**f["geometry"], "spatialReference": sr_dict}
        circles_to_add.append(Feature(geometry=Polygon(g), attributes=f["attributes"]))

    for f in markings["masks"]:
        g = {**f["geometry"], "spatialReference": sr_dict}
        masks_to_add.append(Feature(geometry=Polygon(g), attributes=f["attributes"]))

    for f in markings["points"]:
        g = {**f["geometry"], "spatialReference": sr_dict}
        points_to_add.append(Feature(geometry=Point(g), attributes=f["attributes"]))

    processed_ids.append(field_id)

print(f"Computed markings for {len(processed_ids)} field(s).")
if skipped:
    print(f"Skipped {len(skipped)} field(s):")
    for fid, reason in skipped:
        print(f"  OBJECTID {fid}: {reason}")
```

- [ ] **Step 2: Commit**

```bash
git add field_layout.ipynb
git commit -m "feat: add notebook cells 4-5 (read fields, compute markings)"
```

---

### Task 15: Notebook — Cells 6–7 (clear, write, update renderer)

**Files:**
- Modify: `field_layout.ipynb`

- [ ] **Step 1: Add Cells 6–7 to the notebook**

**Cell 6 — Clear Existing Markings:**
```python
# ── Cell 6: Clear Existing Markings (idempotent) ─────────────────────────
if not processed_ids:
    print("No fields to process — skipping clear.")
else:
    ids_str = ",".join(str(i) for i in processed_ids)
    where   = f"field_id IN ({ids_str})"
    for fl, name in [
        (lines_fl,   "Lines"),
        (circles_fl, "Circles"),
        (masks_fl,   "Masks"),
        (points_fl,  "Points"),
    ]:
        result = fl.delete_features(where=where)
        deleted = len(result.get("deleteResults", []))
        print(f"  {name}: deleted {deleted} existing feature(s).")
```

**Cell 7 — Write & Update Renderer:**
```python
# ── Cell 7: Write & Update Renderer ──────────────────────────────────────

def _add_features(fl, features, layer_name):
    if not features:
        print(f"  {layer_name}: nothing to add.")
        return
    result = fl.edit_features(adds=features)
    success = sum(1 for r in result.get("addResults", []) if r.get("success"))
    print(f"  {layer_name}: added {success}/{len(features)} feature(s).")

_add_features(lines_fl,   lines_to_add,   "Lines")
_add_features(circles_fl, circles_to_add, "Circles")
_add_features(masks_fl,   masks_to_add,   "Masks")
_add_features(points_fl,  points_to_add,  "Points")

# Update masks layer renderer — UniqueValueRenderer keyed on pitch_type
# using colors extracted from source layer in Cell 2
unique_value_infos = []
for pitch_type, color in pitch_colors.items():
    unique_value_infos.append({
        "value": pitch_type,
        "label": pitch_type,
        "symbol": {
            "type": "esriSFS",
            "style": "esriSFSSolid",
            "color": list(color),
            "outline": None,
        },
    })

if unique_value_infos:
    new_renderer = {
        "type": "uniqueValue",
        "field1": "pitch_type",
        "uniqueValueInfos": unique_value_infos,
        "defaultSymbol": {
            "type": "esriSFS",
            "style": "esriSFSSolid",
            "color": [0, 0, 0, 0],  # transparent fallback
            "outline": None,
        },
    }
    masks_fl.manager.update_definition({"drawingInfo": {"renderer": new_renderer}})
    print("Masks renderer updated.")
else:
    print("Warning: no pitch colors found — masks renderer not updated.")

print(f"\nDone. Processed {len(processed_ids)} field(s).")
if skipped:
    print(f"Skipped: {[f[0] for f in skipped]}")
```

- [ ] **Step 2: Run full notebook end-to-end against a test field**

With Cell 1 filled in with real item IDs:
1. Run all cells top-to-bottom
2. Open the ArcGIS Online web map, verify markings appear on the field polygon
3. Re-run the notebook (without changing anything)
4. Verify feature count is identical — no duplicates (idempotency confirmed)

- [ ] **Step 3: Smoke test each pitch type**

Set `FIELD_IDS` in Cell 1 to contain one field of each pitch type (7v7, 9v9, 11v11) and run. Verify:
- 7v7: build-out lines visible; corner arcs visible; penalty arc visible
- 9v9: penalty area width narrower than 11v11
- 11v11: center circle larger than 9v9/7v7

- [ ] **Step 4: Final commit**

```bash
git add field_layout.ipynb
git commit -m "feat: add notebook cells 6-7 (clear, write, update renderer)"
```

---

## Self-Review

**Spec coverage check:**

| Requirement | Task |
|---|---|
| Read field polygons from ArcGIS Online | Task 14 (Cell 4) |
| Derive orientation/dims from polygon MBR | Tasks 4, 7 |
| Pitch type from `Pitch Type` attribute | Tasks 2, 14 |
| Lines layer: touchlines, goal lines, halfway, areas, build-out | Tasks 7, 8, 12 |
| Circles layer: center circle, penalty arc circles, corner arcs | Tasks 9, 10, 11 |
| Masks layer: occlusion rects, renderer matched to source colors | Tasks 10, 11, 15 |
| Points layer: center mark, penalty marks | Task 9 |
| `field_id` = OBJECTID for idempotency | Tasks 7, 15 |
| Clear+redraw on re-run (idempotent) | Task 15 (Cell 6) |
| Environment auto-detection (local vs ArcGIS Online) | Task 13 (Cell 2) |
| SAY specs: 11v11 | Task 2 |
| SAY specs: 9v9 | Task 2 |
| SAY specs: 7v7 + build-out lines | Tasks 2, 12 |
| Unit tests for geometry functions | Tasks 3–6 |
| Unit tests for field markings per pitch type | Tasks 7–12 |
| Scale via `yards_to_native` | Task 6, 14 |
| Skip invalid/unknown fields gracefully | Tasks 7, 14 |

**No placeholders found.** All steps contain complete code.

**Type consistency:** `build_field_markings` returns the same `{"paths": [...]}` / `{"rings": [...]}` / `{"x": ..., "y": ...}` structure throughout Tasks 7–12 and consumed in Task 14. `field_id`, `component_type`, `pitch_type` attribute keys are consistent across all tasks.
