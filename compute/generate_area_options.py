"""
Generates the area options JSON for embedding in app.js.
Run: python generate_area_options.py > www/areas.js
"""
import json
from areas import get_areas, REGIONS

areas = get_areas()
options = []
for a in sorted(areas, key=lambda x: x['name']):
    options.append({
        'code': a['code'],
        'name': a['name'],
        'region': a['region'],
        'regionLabel': REGIONS.get(a['region'], a['region']),
        'rent2br': a['rent_2br'],
        'ctAnnual': a['ct_annual'],
    })

print("window.AREA_OPTIONS = " + json.dumps(options, indent=2) + ";")
