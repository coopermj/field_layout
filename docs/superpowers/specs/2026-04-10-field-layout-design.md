# Field Layout Design Spec
**Date:** 2026-04-10
**Status:** Approved

## Overview

An ArcGIS Notebook (`.ipynb`) that reads soccer field polygons from ArcGIS Online and draws SAY-compliant field markings into four output feature layers. Developed and debugged locally via Jupyter, then uploaded to ArcGIS Online for production use.

---

## Input

- **Source**: ArcGIS Online feature layer containing field polygons
- **Key attribute**: `Pitch Type` — one of `7v7`, `9v9`, `11v11`
- **Geometry**: Polygon representing the field boundary

---

## Output Layers

Four feature layers in ArcGIS Online, rendered in this order (bottom → top):

| Layer | Geometry | Contents |
|---|---|---|
| Field Markings — Lines | Polyline | Touchlines, goal lines, halfway line, penalty area outline, goal area outline, build-out lines (7v7 only) |
| Field Markings — Circles | Polygon | Center circle, penalty arc circles, corner arc circles (full circles, hollow fill) |
| Field Markings — Masks | Polygon | Occlusion rectangles to hide unwanted arc portions; fill color matched to field polygon background |
| Field Markings — Points | Point | Center mark, penalty marks (×2) |

All features carry `field_id` (the source polygon's `OBJECTID`) and `component_type` attributes.

The notebook auto-creates any output layer that doesn't exist yet, with the correct schema and spatial reference matching the input layer.

---

## Geometry Approach

**Polygon-derived** — no extra attributes required on the source polygon.

1. Compute the minimum bounding rectangle (MBR) of the input polygon
2. Extract: center point, long-axis orientation angle, length, width
3. Look up SAY specs for the pitch type
4. Generate all marking geometries in a local coordinate system (origin = center, x = along touchline)
5. Rotate and translate to real-world coordinates

### Arc / Circle Rendering

- **Circles** (center circle): stored as polygon geometry, styled hollow
- **Arcs** (penalty arc, corner arcs): stored as full circle polygons in the Circles layer, with corresponding occlusion mask rectangles in the Masks layer rendered on top
- Masks layer uses a `UniqueValueRenderer` keyed on `pitch_type`, with fill colors read from the source field polygon layer's renderer at runtime

---

## SAY Field Specifications

> **Range dimensions**: Some components (goal area width, penalty area width) vary because they depend on goal width, which itself has a recommended range. Where a range is shown, the notebook uses the **lower bound** of the range as the canonical dimension. This matches the SAY minimum and produces consistent output across all fields of the same pitch type.



### 11v11 — Full-Sided (14U / Kickers, 16U / Minors, 19U / Seniors)

| Component | Dimension |
|---|---|
| Field | 80–130 yds × 50–100 yds |
| Goal area | 20 yds wide × 6 yds deep |
| Penalty area | 44 yds wide × 18 yds deep |
| Penalty mark | 12 yds from goal line |
| Penalty arc radius | 10 yds |
| Center circle radius | 10 yds |
| Corner arc radius | 1 yd |

### 9v9 — Small-Sided (12U / Strikers)

| Component | Dimension |
|---|---|
| Field | 70–80 yds × 45–55 yds |
| Goal area | 16–17 yds wide × 5 yds deep |
| Penalty area | 36–37 yds wide × 14 yds deep |
| Penalty mark | 10 yds from goal line |
| Penalty arc radius | 8 yds |
| Center circle radius | 8 yds |
| Corner arc radius | 1 yd |

### 7v7 — Small-Sided (8U / Passers, 10U / Wings)

| Component | Dimension |
|---|---|
| Field | 55–65 yds × 35–45 yds |
| Goal area | 8–10 yds wide × 4 yds deep |
| Penalty area | 24–26 yds wide × 12 yds deep |
| Penalty mark | 10 yds from goal line |
| Penalty arc radius | 8 yds |
| Center circle radius | 8 yds |
| Corner arc radius | 1 yd |
| Build-out lines | 2 lines, full width, equidistant between halfway line and penalty area |

---

## Notebook Structure

| Cell | Purpose |
|---|---|
| 1 — Configuration | Layer item IDs, optional `field_ids` filter (empty = all fields). Environment detection: `GIS("home")` in ArcGIS Online, `GIS("https://www.arcgis.com")` locally. |
| 2 — Connect & Load | Connect to GIS, load four output layers, read source layer renderer → extract fill color per pitch type |
| 3 — SAY Specs | Hardcoded dictionary of SAY dimensions per pitch type |
| 4 — Geometry Functions | Pure functions: `min_bounding_rect`, `make_rectangle`, `make_circle`, `make_arc_masks`, `rotate_translate` |
| 5 — Read Fields | Query field polygons; apply `field_ids` filter if set |
| 6 — Compute Markings | For each field: MBR → SAY lookup → generate all geometries; collect into four feature lists |
| 7 — Clear Existing | Delete features in all output layers where `field_id` is in current batch (idempotent) |
| 8 — Write & Update Renderer | Add new features to all output layers; update Masks layer `UniqueValueRenderer` with colors from Cell 2; print summary |

---

## Idempotency

Each feature carries a `field_id` attribute. Re-running the notebook deletes all existing features for the processed field IDs before writing new ones. Safe to re-run after polygon edits.

---

## Error Handling

| Situation | Behavior |
|---|---|
| Unknown `Pitch Type` value | Skip field, collect warning, print in summary |
| Polygon with < 3 vertices or zero area | Skip field, collect warning, print in summary |
| Output layer doesn't exist | Auto-create with correct schema |
| Source renderer has no color for a pitch type | Fall back to transparent mask fill, log warning |
| ArcGIS API write failure | Raise — surface traceback in notebook output |

---

## Testing

**Unit tests** (`tests/test_geometry.py`) — pure Python, no ArcGIS dependency, run with `pytest`:
- `min_bounding_rect` — verify center, angle, dimensions from known polygons
- `make_rectangle` — verify corner coordinates and rotation
- `make_circle` — verify radius and point count
- `rotate_translate` — verify transformation accuracy
- Per-pitch-type assertions: penalty mark distance, penalty area dims, center circle radius, build-out line placement (7v7)

**Visual smoke test** — run notebook locally against one field of each pitch type; visually confirm markings align in the web map; re-run to confirm idempotency.

---

## Local Development Environment

- Python 3.13, virtual environment at `.venv/`
- Dependencies: `arcgis`, `jupyter`, `ipykernel` (installed via pip)
- Activate: `source .venv/bin/activate`
- Run notebook: `jupyter notebook field_layout.ipynb`
- Run tests: `pytest tests/`

---

## Files

```
field_layout/
├── field_layout.ipynb       # Main notebook
├── tests/
│   └── test_geometry.py     # Unit tests for geometry functions
├── .venv/                   # Local Python environment
├── field_rules.pdf          # SAY Soccer Playing Laws Rulebook
└── docs/superpowers/specs/
    └── 2026-04-10-field-layout-design.md
```
