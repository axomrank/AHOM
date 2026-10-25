#!/usr/bin/env python3
"""Build optional reference outlines. Requires Shapely; not needed by the site build.

Usage: python3 tools/import_boundaries.py LOCAL_KMZ INDIA_SOI_GEOJSON
India source: https://github.com/datameet/maps/blob/master/Country/india-soi.geojson
"""
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile
from shapely import make_valid
from shapely.geometry import Polygon, shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parent.parent
ns = {'k': 'http://www.opengis.net/kml/2.2'}


def rings(geometry, tolerance):
    geometry = geometry.simplify(tolerance, preserve_topology=True)
    polygons = [geometry] if geometry.geom_type == 'Polygon' else geometry.geoms
    return [[[round(lat, 5), round(lon, 5)] for lon, lat in p.exterior.coords]
            for p in polygons if p.geom_type == 'Polygon']


def main():
    kmz, india = map(Path, sys.argv[1:])
    with zipfile.ZipFile(kmz) as z:
        kml = ET.fromstring(z.read('doc.kml'))
    polygons = []
    for folder in kml.findall('.//k:Folder', ns):
        if folder.findtext('k:name', namespaces=ns) != 'Assam Districts':
            continue
        for place in folder.findall('k:Placemark', ns):
            if not place.findtext('k:name', default='', namespaces=ns).isupper():
                continue
            for ring in place.findall('.//k:outerBoundaryIs//k:coordinates', ns):
                points = [tuple(map(float, p.split(',')[:2])) for p in ring.text.split()]
                if len(points) >= 4:
                    polygons.append(make_valid(Polygon(points)))
    assam = unary_union(polygons)
    country = unary_union([make_valid(shape(f['geometry'])) for f in json.loads(india.read_text())['features']])
    data = {
        'note': 'Optional modern geographic reference layers, not historical Ahom borders. Coordinates are [latitude, longitude]. Districts use the 33-unit local source vintage.',
        'assam': {'name': 'Assam boundary', 'rings': rings(assam, .003),
                  'source': 'Local APP Dist + Rivers (simplified).kmz; outer district polygons dissolved before simplification',
                  'sha256': hashlib.sha256(kmz.read_bytes()).hexdigest()},
        'india': {'name': 'India boundary', 'rings': rings(country, .008),
                  'source': 'DataMeet Community Maps, india-soi.geojson; Survey of India / Census 2011 derived',
                  'url': 'https://github.com/datameet/maps/blob/master/Country/india-soi.geojson',
                  'license': 'CC BY-SA 2.5 / ODbL, as recorded by DataMeet',
                  'sha256': hashlib.sha256(india.read_bytes()).hexdigest()}
    }
    (ROOT / 'assets/maps/boundaries.json').write_text(json.dumps(data, separators=(',', ':')) + '\n')
    print({key: sum(map(len, data[key]['rings'])) for key in ['assam', 'india']})


if __name__ == '__main__':
    main()
