"""
ONS Data loading and area cost lookup.

Sources:
- ONS Private Rental Market Statistics (quarterly)
- ONS Council Tax estimates per Local Authority
- ONS Built-Up Areas list (2021 census)
"""

import json
import math
import os
from pathlib import Path
from typing import Optional

# ─── Hardcoded area data for v1 ───────────────────────────────────────────────
# In production, this is loaded from data/areas.json
# Format: {bua_code: {name, region, lat, lon, rent_1br, rent_2br, rent_3br, ct_band, ct_annual}}

# Representative sample of UK areas (postcodes → BUAs)
# In v1 we embed a sample; full data is loaded from data/areas.json in production


def load_areas(data_dir: Path) -> dict:
    """Load areas data from JSON file."""
    areas_file = data_dir / "areas.json"
    if areas_file.exists():
        with open(areas_file) as f:
            return json.load(f)
    return {}


def get_uk_average() -> dict:
    """
    Returns a representative 'UK average' area for fallback.
    """
    return {
        'name': 'United Kingdom (Average)',
        'region': 'UK',
        'lat': 54.0,
        'lon': -2.0,
        'rent_1br': 750.0,
        'rent_2br': 950.0,
        'rent_3br': 1250.0,
        'ct_band': 'C',
        'ct_annual': 1800.0,
        'utilities': 1200.0,
    }


# ─── Council Tax bands (annual, representative average) ──────────────────────
# These vary enormously by LA. In v1, we use regional averages.

COUNCIL_TAX_BANDS = {
    'A': 900,
    'B': 1100,
    'C': 1400,
    'D': 1700,
    'E': 2100,
    'F': 2600,
    'G': 3100,
    'H': 3800,
}


def estimate_council_tax_from_rent(monthly_rent: float) -> float:
    """
    Rough estimation: council tax is roughly proportional to property value,
    which correlates with rent. Use a simplified ratio.
    """
    # Average UK rent for a 2br is ~£950 PCM
    # Average council tax for band C is ~£1,700/year
    # Ratio: 1700 / 950 ≈ 1.79
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
