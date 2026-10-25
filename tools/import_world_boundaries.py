#!/usr/bin/env python3
"""Import Natural Earth 10m admin-0 countries. Requires Shapely only for import.

Usage: python3 tools/import_world_boundaries.py ne_10m_admin_0_countries.geojson
"""
import hashlib
import json
from pathlib import Path
import sys
from shapely.geometry import shape
from import_boundaries import rings

source = Path(sys.argv[1])
features = json.loads(source.read_text())['features']
countries = []
for feature in features:
    p = feature['properties']
    countries.append({'id': p['ADM0_A3'], 'name': p['ADMIN'],
                      'geo': [p['LABEL_Y'], p['LABEL_X']],
                      'rings': rings(shape(feature['geometry']), .012)})
data = {'source': 'Natural Earth 1:10m admin-0 countries; simplified 0.012 degrees with topology preservation',
        'url': 'https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-admin-0-countries/',
        'license': 'Public domain',
        'note': 'Modern reference outlines, including coastlines and territories. Natural Earth uses de facto boundaries by default; these may differ from the separately sourced India outline. Not historical borders.',
        'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'countries': countries}
target = Path(__file__).resolve().parent.parent / 'assets/maps/world.json'
target.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n')
print(f'{len(countries)} country/territory features; {target.stat().st_size:,} bytes')
