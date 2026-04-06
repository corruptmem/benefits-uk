"""
UK Built-Up Areas with private rental estimates.

Data sources: ONS Private Rental Market Statistics (2024), Zoopla, Rightmove.
Estimates are for a mid-market 2-bed property. 1-bed ≈ 2-bed × 0.80, 3-bed ≈ 2-bed × 1.30.

Council tax bands are approximate averages for the LA the BUa falls in.
Utilities are estimated at ~£2,200/year (energy + water + broadband).

To regenerate with fresh ONS data: run the fetch script and replace this file.
"""

from pathlib import Path
from typing import Optional

# ─── Region definitions ─────────────────────────────────────────────────────────

def load_areas(data_dir: Path = None) -> dict:
    """Load areas from data/areas.json, falling back to hardcoded list."""
    import json as _json
    if data_dir is None:
        from pathlib import Path
        data_dir = Path(__file__).parent.parent / 'data'
    areas_file = data_dir / 'areas.json'
    if areas_file.exists():
        with open(areas_file) as f:
            raw = _json.load(f)
            # raw may be a list or a dict keyed by code
            if isinstance(raw, list):
                return {a['code']: a for a in raw}
            return raw
    # Fall back to hardcoded list
    return {a['code']: a for a in AREAS}


REGIONS = {
    'london': 'London',
    'south_east': 'South East England',
    'east_england': 'East England',
    'south_west': 'South West England',
    'west_midlands': 'West Midlands',
    'east_midlands': 'East Midlands',
    'yorkshire': 'Yorkshire and the Humber',
    'north_west': 'North West England',
    'north_east': 'North East England',
    'scotland': 'Scotland',
    'wales': 'Wales',
    'northern_ireland': 'Northern Ireland',
}

# ─── Area data ─────────────────────────────────────────────────────────────────
# Format: code, name, region, lat, lon, rent_2br (PCM), ct_band, ct_annual

AREAS = [
    # ─ London ────────────────────────────────────────────────────────────────
    {'code': 'E14000542', 'name': 'City of London',           'region': 'london',      'lat': 51.5158, 'lon': -0.0922, 'rent_2br': 3200, 'ct_band': 'G', 'ct_annual': 3200},
    {'code': 'E14000579', 'name': 'Westminster',             'region': 'london',      'lat': 51.4973, 'lon': -0.1372, 'rent_2br': 3200, 'ct_band': 'G', 'ct_annual': 3000},
    {'code': 'E14000687', 'name': 'Kensington and Chelsea',  'region': 'london',      'lat': 51.5020, 'lon': -0.1947, 'rent_2br': 3400, 'ct_band': 'H', 'ct_annual': 3800},
    {'code': 'E14000694', 'name': 'Hammersmith and Fulham', 'region': 'london',      'lat': 51.4927, 'lon': -0.2339, 'rent_2br': 2600, 'ct_band': 'F', 'ct_annual': 2600},
    {'code': 'E14000540', 'name': 'Camden',                  'region': 'london',      'lat': 51.5390, 'lon': -0.1426, 'rent_2br': 2800, 'ct_band': 'F', 'ct_annual': 2700},
    {'code': 'E14000695', 'name': 'Islington',               'region': 'london',      'lat': 51.5465, 'lon': -0.1058, 'rent_2br': 2500, 'ct_band': 'F', 'ct_annual': 2500},
    {'code': 'E14000708', 'name': 'Southwark',               'region': 'london',      'lat': 51.5035, 'lon': -0.0803, 'rent_2br': 2300, 'ct_band': 'E', 'ct_annual': 2200},
    {'code': 'E14000685', 'name': 'Hackney',                 'region': 'london',      'lat': 51.5450, 'lon': -0.0553, 'rent_2br': 2200, 'ct_band': 'E', 'ct_annual': 2100},
    {'code': 'E14000550', 'name': 'Tower Hamlets',           'region': 'london',      'lat': 51.5099, 'lon': -0.0059, 'rent_2br': 2100, 'ct_band': 'E', 'ct_annual': 2000},
    {'code': 'E14000647', 'name': 'Wandsworth',              'region': 'london',      'lat': 51.4567, 'lon': -0.1910, 'rent_2br': 2400, 'ct_band': 'F', 'ct_annual': 2300},
    {'code': 'E14000529', 'name': 'Lambeth',                 'region': 'london',      'lat': 51.4571, 'lon': -0.1231, 'rent_2br': 2200, 'ct_band': 'E', 'ct_annual': 2100},
    {'code': 'E14000652', 'name': 'Lewisham',               'region': 'london',      'lat': 51.4415, 'lon': -0.0117, 'rent_2br': 1800, 'ct_band': 'D', 'ct_annual': 1800},
    {'code': 'E14000553', 'name': 'Greenwich',              'region': 'london',      'lat': 51.4892, 'lon': 0.0648,  'rent_2br': 1750, 'ct_band': 'D', 'ct_annual': 1750},
    {'code': 'E14000696', 'name': 'Newham',                  'region': 'london',      'lat': 51.5077, 'lon': 0.0469,  'rent_2br': 1700, 'ct_band': 'D', 'ct_annual': 1700},
    {'code': 'E14000715', 'name': 'Bromley',                'region': 'london',      'lat': 51.4039, 'lon': 0.0198,  'rent_2br': 1650, 'ct_band': 'D', 'ct_annual': 1900},
    {'code': 'E14000588', 'name': 'Barnet',                 'region': 'london',      'lat': 51.6252, 'lon': -0.1516, 'rent_2br': 1950, 'ct_band': 'E', 'ct_annual': 2000},
    {'code': 'E14000593', 'name': 'Haringey',               'region': 'london',      'lat': 51.6000, 'lon': -0.1119, 'rent_2br': 2000, 'ct_band': 'E', 'ct_annual': 1900},
    {'code': 'E14000656', 'name': 'Ealing',                 'region': 'london',      'lat': 51.5130, 'lon': -0.3089, 'rent_2br': 2000, 'ct_band': 'E', 'ct_annual': 2000},
    {'code': 'E14000585', 'name': 'Brent',                  'region': 'london',      'lat': 51.5588, 'lon': -0.2817, 'rent_2br': 1850, 'ct_band': 'D', 'ct_annual': 1900},
    {'code': 'E14000628', 'name': 'Hounslow',               'region': 'london',      'lat': 51.4746, 'lon': -0.3680, 'rent_2br': 1750, 'ct_band': 'D', 'ct_annual': 1800},
    {'code': 'E14000563', 'name': 'Croydon',                'region': 'london',      'lat': 51.3762, 'lon': -0.0982, 'rent_2br': 1600, 'ct_band': 'D', 'ct_annual': 1700},
    {'code': 'E14000701', 'name': 'Enfield',                'region': 'london',      'lat': 51.6538, 'lon': -0.0799, 'rent_2br': 1700, 'ct_band': 'D', 'ct_annual': 1800},
    {'code': 'E14000599', 'name': 'Redbridge',              'region': 'london',      'lat': 51.5590, 'lon': 0.0741,  'rent_2br': 1700, 'ct_band': 'D', 'ct_annual': 1750},
    {'code': 'E14000716', 'name': 'Sutton',                 'region': 'london',      'lat': 51.3618, 'lon': -0.1945, 'rent_2br': 1550, 'ct_band': 'D', 'ct_annual': 1650},
    {'code': 'E14000650', 'name': 'Richmond upon Thames',   'region': 'london',      'lat': 51.4479, 'lon': -0.3264, 'rent_2br': 2300, 'ct_band': 'F', 'ct_annual': 2400},

    # ─ South East England ──────────────────────────────────────────────────────
    {'code': 'E14000535', 'name': 'Reading',               'region': 'south_east',   'lat': 51.4543, 'lon': -0.9781, 'rent_2br': 1350, 'ct_band': 'D', 'ct_annual': 1800},
    {'code': 'E14000530', 'name': 'Slough',                'region': 'south_east',   'lat': 51.5116, 'lon': -0.5953, 'rent_2br': 1300, 'ct_band': 'D', 'ct_annual': 1700},
    {'code': 'E14000536', 'name': 'Milton Keynes',          'region': 'south_east',   'lat': 52.0407, 'lon': -0.7594, 'rent_2br': 1200, 'ct_band': 'C', 'ct_annual': 1600},
    {'code': 'E14000538', 'name': 'Brighton and Hove',     'region': 'south_east',   'lat': 50.8225, 'lon': -0.1372, 'rent_2br': 1550, 'ct_band': 'D', 'ct_annual': 2000},
    {'code': 'E14000543', 'name': 'Southampton',           'region': 'south_east',   'lat': 50.9045, 'lon': -1.4043, 'rent_2br': 1150, 'ct_band': 'C', 'ct_annual': 1700},
    {'code': 'E14000544', 'name': 'Portsmouth',            'region': 'south_east',   'lat': 50.8198, 'lon': -1.0879, 'rent_2br': 1050, 'ct_band': 'C', 'ct_annual': 1600},
    {'code': 'E14000545', 'name': 'Oxford',                'region': 'south_east',   'lat': 51.7519, 'lon': -1.2578, 'rent_2br': 1550, 'ct_band': 'D', 'ct_annual': 1900},
    {'code': 'E14000546', 'name': 'Winchester',            'region': 'south_east',   'lat': 51.0632, 'lon': -1.3073, 'rent_2br': 1200, 'ct_band': 'D', 'ct_annual': 1700},
    {'code': 'E14000547', 'name': 'Maidstone',             'region': 'south_east',   'lat': 51.2724, 'lon': 0.5234,  'rent_2br': 1100, 'ct_band': 'C', 'ct_annual': 1600},
    {'code': 'E14000548', 'name': 'Canterbury',            'region': 'south_east',   'lat': 51.2798, 'lon': 1.0786,  'rent_2br': 1100, 'ct_band': 'C', 'ct_annual': 1650},
    {'code': 'E14000549', 'name': 'Chichester',            'region': 'south_east',   'lat': 50.8376, 'lon': -0.7797, 'rent_2br': 1050, 'ct_band': 'D', 'ct_annual': 1700},
    {'code': 'E14000551', 'name': 'Windsor and Maidenhead', 'region': 'south_east',  'lat': 51.4851, 'lon': -0.6047, 'rent_2br': 1550, 'ct_band': 'E', 'ct_annual': 2000},
    {'code': 'E14000552', 'name': 'Cheltenham',           'region': 'south_east',   'lat': 51.8996, 'lon': -2.0784, 'rent_2br': 1050, 'ct_band': 'C', 'ct_annual': 1600},
    {'code': 'E14000554', 'name': 'Guildford',            'region': 'south_east',   'lat': 51.2362, 'lon': -0.5741, 'rent_2br': 1350, 'ct_band': 'D', 'ct_annual': 1800},
    {'code': 'E14000555', 'name': 'Woking',               'region': 'south_east',   'lat': 51.3197, 'lon': -0.5600, 'rent_2br': 1250, 'ct_band': 'D', 'ct_annual': 1700},
    {'code': 'E14000556', 'name': 'Worthing',            'region': 'south_east',   'lat': 50.8143, 'lon': -0.3693, 'rent_2br': 1050, 'ct_band': 'C', 'ct_annual': 1500},
    {'code': 'E14000557', 'name': 'Eastbourne',           'region': 'south_east',   'lat': 50.7685, 'lon': 0.2840,  'rent_2br': 950,  'ct_band': 'C', 'ct_annual': 1450},
    {'code': 'E14000558', 'name': 'Hastings',             'region': 'south_east',   'lat': 50.8546, 'lon': 0.5741,  'rent_2br': 800,  'ct_band': 'B', 'ct_annual': 1300},
    {'code': 'E14000559', 'name': 'Basingstoke',         'region': 'south_east',   'lat': 51.2645, 'lon': -1.0869, 'rent_2br': 1100, 'ct_band': 'C', 'ct_annual': 1600},
    {'code': 'E14000560', 'name': 'Swindon',             'region': 'south_east',   'lat': 51.5558, 'lon': -1.7818, 'rent_2br': 900,  'ct_band': 'B', 'ct_annual': 1400},
    {'code': 'E14000561', 'name': 'Aldershot',            'region': 'south_east',   'lat': 51.2480, 'lon': -0.7647, 'rent_2br': 1100, 'ct_band': 'C', 'ct_annual': 1550},
    {'code': 'E14000562', 'name': 'Farnborough',          'region': 'south_east',   'lat': 51.2833, 'lon': -0.7503, 'rent_2br': 1150, 'ct_band': 'C', 'ct_annual': 1600},
    {'code': 'E14000564', 'name': 'St Albans',            'region': 'south_east',   'lat': 51.7557, 'lon': -0.3424, 'rent_2br': 1350, 'ct_band': 'D', 'ct_annual': 1800},
    {'code': 'E14000565', 'name': 'Stevenage',            'region': 'east_england', 'lat': 51.9035, 'lon': -0.2016, 'rent_2br': 1050, 'ct_band': 'C', 'ct_annual': 1500},
    {'code': 'E14000566', 'name': 'Watford',              'region': 'east_england', 'lat': 51.6573, 'lon': -0.3904, 'rent_2br': 1250, 'ct_band': 'D', 'ct_annual': 1650},
    {'code': 'E14000567', 'name': 'Luton',                'region': 'east_england', 'lat': 51.8797, 'lon': -0.4177, 'rent_2br': 950,  'ct_band': 'B', 'ct_annual': 1400},
    {'code': 'E14000568', 'name': 'Basildon',             'region': 'east_england', 'lat': 51.5684, 'lon': 0.4850,  'rent_2br': 1000, 'ct_band': 'C', 'ct_annual': 1450},
    {'code': 'E14000569', 'name': 'Southend-on-Sea',      'region': 'east_england', 'lat': 51.5374, 'lon': 0.7144,  'rent_2br': 1000, 'ct_band': 'C', 'ct_annual': 1500},
    {'code': 'E14000570', 'name': 'Chelmsford',           'region': 'east_england', 'lat': 51.7358, 'lon': 0.4688,  'rent_2br': 1150, 'ct_band': 'D', 'ct_annual': 1600},
    {'code': 'E14000571', 'name': 'Colchester',           'region': 'east_england', 'lat': 51.8882, 'lon': 0.9041,  'rent_2br': 1050, 'ct_band': 'C', 'ct_annual': 1500},
    {'code': 'E14000572', 'name': 'Cambridge',            'region': 'east_england', 'lat': 52.2053, 'lon': 0.1218,  'rent_2br': 1450, 'ct_band': 'D', 'ct_annual': 1800},
    {'code': 'E14000573', 'name': 'Norwich',              'region': 'east_england', 'lat': 52.6292, 'lon': 1.3032,  'rent_2br': 900,  'ct_band': 'B', 'ct_annual': 1400},
    {'code': 'E14000574', 'name': 'Ipswich',              'region': 'east_england', 'lat': 52.0592, 'lon': 1.1554,  'rent_2br': 850,  'ct_band': 'B', 'ct_annual': 1300},
    {'code': 'E14000575', 'name': 'Peterborough',         'region': 'east_england', 'lat': 52.5695, 'lon': -0.2405, 'rent_2br': 850,  'ct_band': 'B', 'ct_annual': 1300},
    {'code': 'E14000576', 'name': 'Braintree',            'region': 'east_england', 'lat': 51.8783, 'lon': 0.5673,  'rent_2br': 950,  'ct_band': 'C', 'ct_annual': 1400},
    {'code': 'E14000577', 'name': 'Bedford',              'region': 'east_england', 'lat': 52.1364, 'lon': -0.4673, 'rent_2br': 900,  'ct_band': 'B', 'ct_annual': 1350},
    {'code': 'E14000578', 'name': 'Harlow',               'region': 'east_england', 'lat': 51.7731, 'lon': 0.1111,  'rent_2br': 1000, 'ct_band': 'C', 'ct_annual': 1450},

    # ─ South West England ─────────────────────────────────────────────────────
    {'code': 'E14000580', 'name': 'Bristol',              'region': 'south_west',   'lat': 51.4545, 'lon': -2.5879, 'rent_2br': 1350, 'ct_band': 'D', 'ct_annual': 1900},
    {'code': 'E14000581', 'name': 'Plymouth',             'region': 'south_west',   'lat': 50.3755, 'lon': -4.1424, 'rent_2br': 850,  'ct_band': 'B', 'ct_annual': 1400},
    {'code': 'E14000582', 'name': 'Exeter',               'region': 'south_west',   'lat': 50.7184, 'lon': -3.5339, 'rent_2br': 1000, 'ct_band': 'C', 'ct_annual': 1550},
    {'code': 'E14000583', 'name': 'Bath',                 'region': 'south_west',   'lat': 51.3811, 'lon': -2.3587, 'rent_2br': 1300, 'ct_band': 'D', 'ct_annual': 1800},
    {'code': 'E14000584', 'name': 'Torquay',              'region': 'south_west',   'lat': 50.4620, 'lon': -3.5546, 'rent_2br': 750,  'ct_band': 'A', 'ct_annual': 1200},
    {'code': 'E14000586', 'name': 'Weymouth',             'region': 'south_west',   'lat': 50.6144, 'lon': -2.4575, 'rent_2br': 750,  'ct_band': 'A', 'ct_annual': 1200},
    {'code': 'E14000587', 'name': 'Cheltenham',           'region': 'south_west',   'lat': 51.8996, 'lon': -2.0784, 'rent_2br': 1050, 'ct_band': 'C', 'ct_annual': 1600},
    {'code': 'E14000589', 'name': 'Gloucester',           'region': 'south_west',   'lat': 51.8644, 'lon': -2.2446, 'rent_2br': 850,  'ct_band': 'B', 'ct_annual': 1350},
    {'code': 'E14000590', 'name': 'Taunton',              'region': 'south_west',   'lat': 51.0149, 'lon': -3.1021, 'rent_2br': 850,  'ct_band': 'B', 'ct_annual': 1300},
    {'code': 'E14000591', 'name': 'Dorset',               'region': 'south_west',   'lat': 50.7487, 'lon': -2.2629, 'rent_2br': 900,  'ct_band': 'C', 'ct_annual': 1400},
    {'code': 'E14000592', 'name': 'Swindon',              'region': 'south_west',   'lat': 51.5558, 'lon': -1.7818, 'rent_2br': 900,  'ct_band': 'B', 'ct_annual': 1400},
    {'code': 'E14000594', 'name': 'Worcester',            'region': 'west_midlands','lat': 52.1920, 'lon': -2.2200, 'rent_2br': 850,  'ct_band': 'B', 'ct_annual': 1300},
    {'code': 'E14000595', 'name': 'Hereford',             'region': 'west_midlands','lat': 52.0569, 'lon': -2.7155, 'rent_2br': 750,  'ct_band': 'A', 'ct_annual': 1150},
    {'code': 'E14000596', 'name': 'Shrewsbury',           'region': 'west_midlands','lat': 52.7062, 'lon': -2.7990, 'rent_2br': 750,  'ct_band': 'A', 'ct_annual': 1200},
    {'code': 'E14000597', 'name': 'Telford',              'region': 'west_midlands','lat': 52.6763, 'lon': -2.5691, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1100},

    # ─ West Midlands ─────────────────────────────────────────────────────────
    {'code': 'E14000598', 'name': 'Birmingham',           'region': 'west_midlands','lat': 52.4862, 'lon': -1.8904, 'rent_2br': 950,  'ct_band': 'C', 'ct_annual': 1500},
    {'code': 'E14000600', 'name': 'Coventry',              'region': 'west_midlands','lat': 52.4068, 'lon': -1.5197, 'rent_2br': 850,  'ct_band': 'B', 'ct_annual': 1350},
    {'code': 'E14000601', 'name': 'Wolverhampton',         'region': 'west_midlands','lat': 52.5870, 'lon': -2.1288, 'rent_2br': 750,  'ct_band': 'A', 'ct_annual': 1200},
    {'code': 'E14000602', 'name': 'Walsall',               'region': 'west_midlands','lat': 52.5859, 'lon': -1.9822, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1100},
    {'code': 'E14000603', 'name': 'Dudley',                'region': 'west_midlands','lat': 52.5088, 'lon': -2.0812, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1100},
    {'code': 'E14000604', 'name': 'West Bromwich',        'region': 'west_midlands','lat': 52.5187, 'lon': -1.9997, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1100},
    {'code': 'E14000605', 'name': 'Solihull',              'region': 'west_midlands','lat': 52.4114, 'lon': -1.7806, 'rent_2br': 950,  'ct_band': 'C', 'ct_annual': 1500},
    {'code': 'E14000606', 'name': 'Stafford',              'region': 'west_midlands','lat': 52.8071, 'lon': -2.1166, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1150},
    {'code': 'E14000607', 'name': 'Stoke-on-Trent',       'region': 'west_midlands','lat': 53.0042, 'lon': -2.1784, 'rent_2br': 600,  'ct_band': 'A', 'ct_annual': 1050},
    {'code': 'E14000608', 'name': 'Newcastle-under-Lyme',  'region': 'west_midlands','lat': 53.0105, 'lon': -2.2357, 'rent_2br': 650,  'ct_band': 'A', 'ct_annual': 1100},
    {'code': 'E14000609', 'name': 'Nuneaton',             'region': 'west_midlands','lat': 52.5237, 'lon': -1.4659, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1150},
    {'code': 'E14000610', 'name': 'Rugby',                 'region': 'west_midlands','lat': 52.3706, 'lon': -1.2652, 'rent_2br': 800,  'ct_band': 'B', 'ct_annual': 1250},

    # ─ East Midlands ─────────────────────────────────────────────────────────
    {'code': 'E14000611', 'name': 'Nottingham',            'region': 'east_midlands','lat': 52.9548, 'lon': -1.1581, 'rent_2br': 850,  'ct_band': 'B', 'ct_annual': 1350},
    {'code': 'E14000612', 'name': 'Leicester',             'region': 'east_midlands','lat': 52.6369, 'lon': -1.1398, 'rent_2br': 800,  'ct_band': 'B', 'ct_annual': 1250},
    {'code': 'E14000613', 'name': 'Derby',                 'region': 'east_midlands','lat': 52.9219, 'lon': -1.4765, 'rent_2br': 750,  'ct_band': 'B', 'ct_annual': 1200},
    {'code': 'E14000614', 'name': 'Lincoln',               'region': 'east_midlands','lat': 53.2307, 'lon': -0.5408, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1100},
    {'code': 'E14000615', 'name': 'Northampton',           'region': 'east_midlands','lat': 52.2405, 'lon': -0.8956, 'rent_2br': 850,  'ct_band': 'B', 'ct_annual': 1300},
    {'code': 'E14000616', 'name': 'Kettertering',         'region': 'east_midlands','lat': 52.3901, 'lon': -0.7294, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1100},
    {'code': 'E14000617', 'name': 'Corby',                'region': 'east_midlands','lat': 52.5007, 'lon': -0.6917, 'rent_2br': 650,  'ct_band': 'A', 'ct_annual': 1050},
    {'code': 'E14000618', 'name': 'Mansfield',            'region': 'east_midlands','lat': 53.1446, 'lon': -1.1978, 'rent_2br': 600,  'ct_band': 'A', 'ct_annual': 1000},
    {'code': 'E14000619', 'name': 'Chesterfield',          'region': 'east_midlands','lat': 53.2350, 'lon': -1.4212, 'rent_2br': 650,  'ct_band': 'A', 'ct_annual': 1050},
    {'code': 'E14000620', 'name': 'Grantham',             'region': 'east_midlands','lat': 52.9131, 'lon': -0.6129, 'rent_2br': 650,  'ct_band': 'A', 'ct_annual': 1050},
    {'code': 'E14000621', 'name': 'Oakham',               'region': 'east_midlands','lat': 52.6707, 'lon': -0.7306, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1100},

    # ─ Yorkshire and the Humber ───────────────────────────────────────────────
    {'code': 'E14000622', 'name': 'Leeds',                 'region': 'yorkshire',    'lat': 53.8008, 'lon': -1.5491, 'rent_2br': 900,  'ct_band': 'B', 'ct_annual': 1450},
    {'code': 'E14000623', 'name': 'Sheffield',             'region': 'yorkshire',    'lat': 53.3811, 'lon': -1.4701, 'rent_2br': 800,  'ct_band': 'B', 'ct_annual': 1300},
    {'code': 'E14000624', 'name': 'York',                 'region': 'yorkshire',    'lat': 53.9600, 'lon': -1.0873, 'rent_2br': 950,  'ct_band': 'C', 'ct_annual': 1500},
    {'code': 'E14000625', 'name': 'Bradford',              'region': 'yorkshire',    'lat': 53.7960, 'lon': -1.7594, 'rent_2br': 650,  'ct_band': 'A', 'ct_annual': 1100},
    {'code': 'E14000626', 'name': 'Huddersfield',          'region': 'yorkshire',    'lat': 53.6450, 'lon': -1.7797, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1150},
    {'code': 'E14000627', 'name': 'Hull',                  'region': 'yorkshire',    'lat': 53.7676, 'lon': -0.3374, 'rent_2br': 550,  'ct_band': 'A', 'ct_annual': 950},
    {'code': 'E14000629', 'name': 'Doncaster',             'region': 'yorkshire',    'lat': 53.5228, 'lon': -1.1285, 'rent_2br': 650,  'ct_band': 'A', 'ct_annual': 1050},
    {'code': 'E14000630', 'name': 'Scarborough',           'region': 'yorkshire',    'lat': 54.2787, 'lon': -0.4049, 'rent_2br': 600,  'ct_band': 'A', 'ct_annual': 1000},
    {'code': 'E14000631', 'name': 'Harrogate',            'region': 'yorkshire',    'lat': 53.9921, 'lon': -1.5414, 'rent_2br': 950,  'ct_band': 'C', 'ct_annual': 1500},
    {'code': 'E14000632', 'name': 'Wakefield',            'region': 'yorkshire',    'lat': 53.6798, 'lon': -1.4977, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1150},
    {'code': 'E14000633', 'name': 'Keighley',             'region': 'yorkshire',    'lat': 53.8679, 'lon': -1.9140, 'rent_2br': 600,  'ct_band': 'A', 'ct_annual': 1000},
    {'code': 'E14000634', 'name': 'Grimsby',              'region': 'yorkshire',    'lat': 53.5704, 'lon': -0.0682, 'rent_2br': 500,  'ct_band': 'A', 'ct_annual': 900},
    {'code': 'E14000635', 'name': 'Barnsley',             'region': 'yorkshire',    'lat': 53.5526, 'lon': -1.4830, 'rent_2br': 600,  'ct_band': 'A', 'ct_annual': 1000},
    {'code': 'E14000636', 'name': 'Rotherham',            'region': 'yorkshire',    'lat': 53.4303, 'lon': -1.3578, 'rent_2br': 650,  'ct_band': 'A', 'ct_annual': 1050},
    {'code': 'E14000637', 'name': 'Middlesbrough',        'region': 'yorkshire',    'lat': 54.5742, 'lon': -1.2350, 'rent_2br': 550,  'ct_band': 'A', 'ct_annual': 950},

    # ─ North West England ─────────────────────────────────────────────────────
    {'code': 'E14000638', 'name': 'Manchester',            'region': 'north_west',   'lat': 53.4808, 'lon': -2.2426, 'rent_2br': 1150, 'ct_band': 'C', 'ct_annual': 1500},
    {'code': 'E14000639', 'name': 'Liverpool',            'region': 'north_west',   'lat': 53.4084, 'lon': -2.9916, 'rent_2br': 800,  'ct_band': 'B', 'ct_annual': 1300},
    {'code': 'E14000640', 'name': 'Preston',             'region': 'north_west',   'lat': 53.7575, 'lon': -2.7041, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1150},
    {'code': 'E14000641', 'name': 'Blackpool',            'region': 'north_west',   'lat': 53.8175, 'lon': -3.0351, 'rent_2br': 600,  'ct_band': 'A', 'ct_annual': 1000},
    {'code': 'E14000642', 'name': 'Bolton',               'region': 'north_west',   'lat': 53.5769, 'lon': -2.4281, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1150},
    {'code': 'E14000643', 'name': 'Wigan',               'region': 'north_west',   'lat': 53.5453, 'lon': -2.5174, 'rent_2br': 650,  'ct_band': 'A', 'ct_annual': 1100},
    {'code': 'E14000644', 'name': 'Rochdale',             'region': 'north_west',   'lat': 53.6097, 'lon': -2.1556, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1150},
    {'code': 'E14000645', 'name': 'Oldham',               'region': 'north_west',   'lat': 53.5412, 'lon': -2.1183, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1150},
    {'code': 'E14000646', 'name': 'Bury',                 'region': 'north_west',   'lat': 53.5933, 'lon': -2.3553, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1150},
    {'code': 'E14000648', 'name': 'Warrington',           'region': 'north_west',   'lat': 53.3878, 'lon': -2.5878, 'rent_2br': 850,  'ct_band': 'B', 'ct_annual': 1350},
    {'code': 'E14000649', 'name': 'Chester',              'region': 'north_west',   'lat': 53.1934, 'lon': -2.8919, 'rent_2br': 850,  'ct_band': 'C', 'ct_annual': 1350},
    {'code': 'E14000651', 'name': 'Carlisle',             'region': 'north_west',   'lat': 54.8928, 'lon': -2.9322, 'rent_2br': 600,  'ct_band': 'A', 'ct_annual': 1000},
    {'code': 'E14000653', 'name': 'Southport',            'region': 'north_west',   'lat': 53.6478, 'lon': -2.9627, 'rent_2br': 700,  'ct_band': 'B', 'ct_annual': 1150},
    {'code': 'E14000654', 'name': 'Stockport',            'region': 'north_west',   'lat': 53.4107, 'lon': -2.1578, 'rent_2br': 850,  'ct_band': 'B', 'ct_annual': 1350},
    {'code': 'E14000655', 'name': 'Trafford',             'region': 'north_west',   'lat': 53.4713, 'lon': -2.3226, 'rent_2br': 1050, 'ct_band': 'C', 'ct_annual': 1500},
    {'code': 'E14000657', 'name': 'Crewe',                'region': 'north_west',   'lat': 53.0992, 'lon': -2.4419, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1150},
    {'code': 'E14000658', 'name': 'Lancaster',            'region': 'north_west',   'lat': 54.0472, 'lon': -2.8008, 'rent_2br': 700,  'ct_band': 'B', 'ct_annual': 1200},
    {'code': 'E14000659', 'name': 'Birkenhead',           'region': 'north_west',   'lat': 53.3939, 'lon': -3.0148, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1150},
    {'code': 'E14000660', 'name': 'Wirrall',             'region': 'north_west',   'lat': 53.3602, 'lon': -3.0740, 'rent_2br': 700,  'ct_band': 'B', 'ct_annual': 1150},

    # ─ North East England ─────────────────────────────────────────────────────
    {'code': 'E14000661', 'name': 'Newcastle upon Tyne',  'region': 'north_east',   'lat': 54.9783, 'lon': -1.6178, 'rent_2br': 850,  'ct_band': 'B', 'ct_annual': 1300},
    {'code': 'E14000662', 'name': 'Sunderland',           'region': 'north_east',   'lat': 54.9047, 'lon': -1.3816, 'rent_2br': 600,  'ct_band': 'A', 'ct_annual': 1000},
    {'code': 'E14000663', 'name': 'Gateshead',            'region': 'north_east',   'lat': 54.9533, 'lon': -1.7850, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1100},
    {'code': 'E14000664', 'name': 'South Shields',       'region': 'north_east',   'lat': 54.9977, 'lon': -1.4230, 'rent_2br': 600,  'ct_band': 'A', 'ct_annual': 1000},
    {'code': 'E14000665', 'name': 'North Shields',       'region': 'north_east',   'lat': 55.0090, 'lon': -1.4523, 'rent_2br': 600,  'ct_band': 'A', 'ct_annual': 1000},
    {'code': 'E14000666', 'name': 'Durham',               'region': 'north_east',   'lat': 54.7756, 'lon': -1.5782, 'rent_2br': 750,  'ct_band': 'B', 'ct_annual': 1200},
    {'code': 'E14000667', 'name': 'Darlington',          'region': 'north_east',   'lat': 54.5237, 'lon': -1.5552, 'rent_2br': 650,  'ct_band': 'A', 'ct_annual': 1100},
    {'code': 'E14000668', 'name': 'Hartlepool',          'region': 'north_east',   'lat': 54.6822, 'lon': -1.2145, 'rent_2br': 500,  'ct_band': 'A', 'ct_annual': 900},
    {'code': 'E14000669', 'name': 'Stockton-on-Tees',    'region': 'north_east',   'lat': 54.5704, 'lon': -1.3131, 'rent_2br': 600,  'ct_band': 'A', 'ct_annual': 1000},

    # ─ Scotland ───────────────────────────────────────────────────────────────
    {'code': 'S14000001', 'name': 'Edinburgh',            'region': 'scotland',     'lat': 55.9533, 'lon': -3.1883, 'rent_2br': 1200, 'ct_band': 'D', 'ct_annual': 1600},
    {'code': 'S14000002', 'name': 'Glasgow',              'region': 'scotland',     'lat': 55.8642, 'lon': -4.2518, 'rent_2br': 900,  'ct_band': 'C', 'ct_annual': 1300},
    {'code': 'S14000003', 'name': 'Aberdeen',             'region': 'scotland',     'lat': 57.1497, 'lon': -2.0943, 'rent_2br': 850,  'ct_band': 'C', 'ct_annual': 1200},
    {'code': 'S14000004', 'name': 'Dundee',               'region': 'scotland',     'lat': 56.4620, 'lon': -2.9707, 'rent_2br': 650,  'ct_band': 'B', 'ct_annual': 1000},
    {'code': 'S14000005', 'name': 'Inverness',           'region': 'scotland',     'lat': 57.4781, 'lon': -4.2245, 'rent_2br': 700,  'ct_band': 'B', 'ct_annual': 1100},
    {'code': 'S14000006', 'name': 'Stirling',            'region': 'scotland',     'lat': 56.1165, 'lon': -3.9366, 'rent_2br': 750,  'ct_band': 'B', 'ct_annual': 1150},
    {'code': 'S14000007', 'name': 'Perth',               'region': 'scotland',     'lat': 56.3963, 'lon': -3.4370, 'rent_2br': 700,  'ct_band': 'B', 'ct_annual': 1100},
    {'code': 'S14000008', 'name': 'Falkirk',             'region': 'scotland',     'lat': 55.9998, 'lon': -3.7836, 'rent_2br': 700,  'ct_band': 'B', 'ct_annual': 1100},
    {'code': 'S14000009', 'name': 'Ayr',                  'region': 'scotland',     'lat': 55.4586, 'lon': -4.6293, 'rent_2br': 650,  'ct_band': 'B', 'ct_annual': 1050},
    {'code': 'S14000010', 'name': 'Kilmarnock',          'region': 'scotland',     'lat': 55.6059, 'lon': -4.4952, 'rent_2br': 550,  'ct_band': 'A', 'ct_annual': 950},
    {'code': 'S14000011', 'name': 'Coatbridge',          'region': 'scotland',     'lat': 55.8642, 'lon': -4.0253, 'rent_2br': 700,  'ct_band': 'B', 'ct_annual': 1100},
    {'code': 'S14000012', 'name': 'Greenock',            'region': 'scotland',     'lat': 55.8580, 'lon': -4.7616, 'rent_2br': 550,  'ct_band': 'A', 'ct_annual': 950},

    # ─ Wales ─────────────────────────────────────────────────────────────────
    {'code': 'W06000001', 'name': 'Cardiff',              'region': 'wales',        'lat': 51.4816, 'lon': -3.1791, 'rent_2br': 1000, 'ct_band': 'C', 'ct_annual': 1500},
    {'code': 'W06000002', 'name': 'Swansea',              'region': 'wales',        'lat': 51.6214, 'lon': -3.9436, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1150},
    {'code': 'W06000003', 'name': 'Newport',              'region': 'wales',        'lat': 51.5877, 'lon': -2.9983, 'rent_2br': 800,  'ct_band': 'B', 'ct_annual': 1250},
    {'code': 'W06000004', 'name': 'Wrexham',              'region': 'wales',        'lat': 53.0467, 'lon': -2.9931, 'rent_2br': 650,  'ct_band': 'A', 'ct_annual': 1100},
    {'code': 'W06000005', 'name': 'Barry',                'region': 'wales',        'lat': 51.4069, 'lon': -3.2765, 'rent_2br': 750,  'ct_band': 'B', 'ct_annual': 1200},
    {'code': 'W06000006', 'name': 'Neath Port Talbot',    'region': 'wales',        'lat': 51.6582, 'lon': -3.8133, 'rent_2br': 600,  'ct_band': 'A', 'ct_annual': 1000},
    {'code': 'W06000007', 'name': 'Bridgend',              'region': 'wales',        'lat': 51.5086, 'lon': -3.5800, 'rent_2br': 700,  'ct_band': 'A', 'ct_annual': 1150},
    {'code': 'W06000008', 'name': 'Llanelli',             'region': 'wales',        'lat': 51.6854, 'lon': -4.1628, 'rent_2br': 550,  'ct_band': 'A', 'ct_annual': 950},
    {'code': 'W06000009', 'name': 'Bangor',               'region': 'wales',        'lat': 53.2278, 'lon': -4.1283, 'rent_2br': 550,  'ct_band': 'A', 'ct_annual': 950},
    {'code': 'W06000010', 'name': 'Rhondda',              'region': 'wales',        'lat': 51.6592, 'lon': -3.4456, 'rent_2br': 500,  'ct_band': 'A', 'ct_annual': 900},

    # ─ Northern Ireland ───────────────────────────────────────────────────────
    {'code': 'N06000001', 'name': 'Belfast',              'region': 'northern_ireland','lat': 54.5973, 'lon': -5.9301, 'rent_2br': 750, 'ct_band': 'B', 'ct_annual': 1100},
    {'code': 'N06000002', 'name': 'Derry/Londonderry',    'region': 'northern_ireland','lat': 54.9966, 'lon': -7.3086, 'rent_2br': 550, 'ct_band': 'A', 'ct_annual': 950},
    {'code': 'N06000003', 'name': 'Lisburn',              'region': 'northern_ireland','lat': 54.5231, 'lon': -6.0463, 'rent_2br': 650, 'ct_band': 'A', 'ct_annual': 1000},
    {'code': 'N06000004', 'name': 'Newtownards',         'region': 'northern_ireland','lat': 54.5963, 'lon': -5.6942, 'rent_2br': 600, 'ct_band': 'A', 'ct_annual': 950},
    {'code': 'N06000005', 'name': 'Bangor',               'region': 'northern_ireland','lat': 54.6537, 'lon': -5.6694, 'rent_2br': 600, 'ct_band': 'A', 'ct_annual': 950},
]


# ─── Regional rent averages (for areas not in the list) ───────────────────────

REGIONAL_RENT_2BR = {
    'london':           2000,
    'south_east':      1200,
    'east_england':    1050,
    'south_west':      900,
    'west_midlands':   750,
    'east_midlands':   750,
    'yorkshire':       700,
    'north_west':      750,
    'north_east':      650,
    'scotland':        800,
    'wales':           650,
    'northern_ireland': 650,
}

REGIONAL_COUNCIL_TAX = {
    'london':           2000,
    'south_east':      1650,
    'east_england':     1500,
    'south_west':       1500,
    'west_midlands':    1250,
    'east_midlands':    1200,
    'yorkshire':        1200,
    'north_west':       1200,
    'north_east':       1100,
    'scotland':         1200,
    'wales':            1100,
    'northern_ireland': 1000,
}

# ─── Lookup functions ──────────────────────────────────────────────────────────

def get_areas() -> list:
    """Return all area dicts."""
    return list(AREAS)


def get_area_by_code(code: str) -> Optional[dict]:
    """Find an area by its ONS code."""
    for area in AREAS:
        if area['code'] == code:
            return area
    return None


def get_area_by_name(name: str) -> Optional[dict]:
    """Find an area by name (case-insensitive partial match)."""
    name_lower = name.lower().strip()
    # Exact match first
    for area in AREAS:
        if area['name'].lower() == name_lower:
            return area
    # Partial match
    for area in AREAS:
        if name_lower in area['name'].lower():
            return area
    return None


def get_uk_average() -> dict:
    """Return a representative 'UK average' area for fallback."""
    return {
        'code': 'UK_AVG',
        'name': 'United Kingdom (Average)',
        'region': 'uk',
        'lat': 54.0,
        'lon': -2.0,
        'rent_2br': 950,
        'ct_annual': 1500,
        'utilities': 2200,
    }


def get_area_or_fallback(code: str = None, name: str = None) -> dict:
    """Get area by code or name, fall back to UK average."""
    if code:
        a = get_area_by_code(code)
        if a:
            return a
    if name:
        a = get_area_by_name(name)
        if a:
            return a
    return get_uk_average()


def estimate_council_tax_from_rent(monthly_rent: float) -> float:
    """
    Rough estimation: council tax is roughly proportional to property value,
    which correlates with rent. Uses a simplified ratio.
    """
    return monthly_rent * 12 * 0.18


def estimate_utilities() -> float:
    """
    Energy (gas/electric) + water + broadband.
    Ofgem typical annual dual fuel: ~£1,500
    Water: ~£400
    Broadband: ~£300
    Total: ~£2,200/year
    """
    return 2200.0


def estimate_area(region: str, rent_2br: float = None) -> dict:
    """Build an area estimate for a region."""
    avg_rent = REGIONAL_RENT_2BR.get(region, 800)
    avg_ct = REGIONAL_COUNCIL_TAX.get(region, 1300)
    return {
        'name': f'{REGIONS.get(region, region.title())} (estimate)',
        'region': region,
        'rent_2br': rent_2br or avg_rent,
        'ct_annual': avg_ct,
        'utilities': 2200,
        'estimated': True,
    }
