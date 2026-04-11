"""
Creates the four Field Markings output layers in ArcGIS Online.
Run once: python create_output_layers.py
Prints item IDs to paste into Cell 1 of field_layout.ipynb.
"""
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection

COMMON_FIELDS = [
    {
        "name": "field_id",
        "type": "esriFieldTypeInteger",
        "alias": "field_id",
        "nullable": True,
        "editable": True,
        "defaultValue": None,
    },
    {
        "name": "component_type",
        "type": "esriFieldTypeString",
        "alias": "component_type",
        "length": 64,
        "nullable": True,
        "editable": True,
        "defaultValue": None,
    },
    {
        "name": "pitch_type",
        "type": "esriFieldTypeString",
        "alias": "pitch_type",
        "length": 10,
        "nullable": True,
        "editable": True,
        "defaultValue": None,
    },
]

LAYERS = [
    ("Field_Markings_Lines",   "Field Markings — Lines",   "esriGeometryPolyline"),
    ("Field_Markings_Circles", "Field Markings — Circles", "esriGeometryPolygon"),
    ("Field_Markings_Masks",   "Field Markings — Masks",   "esriGeometryPolygon"),
    ("Field_Markings_Points",  "Field Markings — Points",  "esriGeometryPoint"),
]


def create_layer(gis, service_name, title, geometry_type):
    print(f"Creating {title}...")

    item = gis.content.create_service(
        name=service_name,
        service_type="featureService",
        item_properties={
            "title": title,
            "tags": "field layout, soccer, SAY",
            "snippet": f"SAY field markings - {title.split('—')[-1].strip().lower()}",
        },
    )

    flc = FeatureLayerCollection.fromitem(item)
    flc.manager.add_to_definition({
        "layers": [{
            "type": "Feature Layer",
            "name": service_name,
            "geometryType": geometry_type,
            "fields": COMMON_FIELDS,
            "spatialReference": {"wkid": 102100},  # Web Mercator — matches typical ArcGIS Online layers
        }]
    })

    print(f"  ✓ {title}: {item.id}")
    return item.id


def main():
    gis = GIS("https://www.arcgis.com", username="cedaru")
    me = gis.users.me
    if me is None:
        raise RuntimeError("Not authenticated — check your credentials.")
    print(f"Connected as {me.username}\n")

    ids = {}
    for service_name, title, geom_type in LAYERS:
        ids[service_name] = create_layer(gis, service_name, title, geom_type)

    print("\n── Paste these into Cell 1 of field_layout.ipynb ──────────────")
    print(f'LINES_ITEM_ID   = "{ids["Field_Markings_Lines"]}"')
    print(f'CIRCLES_ITEM_ID = "{ids["Field_Markings_Circles"]}"')
    print(f'MASKS_ITEM_ID   = "{ids["Field_Markings_Masks"]}"')
    print(f'POINTS_ITEM_ID  = "{ids["Field_Markings_Points"]}"')


if __name__ == "__main__":
    main()
