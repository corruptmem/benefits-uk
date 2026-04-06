#!/usr/bin/env python3
"""
Fetch ONS Private Rental Market Statistics data.

Downloads the latest quarterly CSV from ONS and converts it to our
areas.json format.

Usage:
  python -m compute.fetch_ons

Requires: pandas, requests
"""

import json
import sys
import zipfile
import io
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("pandas required: pip install pandas")
    sys.exit(1)


# ONS Private Rental Market Statistics — monthly/quarterly data
# URL pattern: https://www.ons.gov.uk/file?uri=...
# We try the quarterly CSV first; fallback to monthly.

URL_QUARTERLY = (
    "https://www.ons.gov.uk/file?uri=/peoplepopulationandcommunity/housing/"
    "datasets/privaterentalmarketsummarystatisticsintheuk/2024/pmsqwinter2024appendixa1.xlsx"
)

URL_MONTHLY = (
    "https://www.ons.gov.uk/economy/inflationandpriceindices/datasets/"
    "privaterentalmarketsummarystatisticsenglandandwalesmonthly"
)


def fetch_ons_data(url: str) -> pd.DataFrame:
    """Download and parse ONS Excel file."""
    import urllib.request

    print(f"Fetching: {url}")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = resp.read()

    print(f"Downloaded {len(data):,} bytes")

    # Try xlsx
    try:
        with open('/tmp/ons_rental.xlsx', 'wb') as f:
            f.write(data)
        df = pd.read_excel('/tmp/ons_rental.xlsx', engine='openpyxl')
        return df
    except Exception as e:
        print(f"Excel parse failed: {e}")
        return pd.DataFrame()


def extract_areas(df: pd.DataFrame) -> list:
    """
    Extract BUAs with median rent from ONS DataFrame.

    ONS PRMS typically has columns:
    ['Region name', 'Local authority code', 'Local authority name',
     'Breakdown', '2019 Q1', '2019 Q2', ...]
    """
    if df.empty:
        return []

    cols = [c for c in df.columns if isinstance(c, str) and c.strip()]
    print(f"Columns: {cols[:10]}")

    # Find the most recent quarter column
    quarter_cols = [c for c in cols if 'Q' in str(c) and any(str(y) in str(c) for y in range(2020, 2026))]
    if not quarter_cols:
        print("No quarter columns found, using first column")
        quarter_cols = [cols[-1]]

    latest_q = sorted(quarter_cols, key=lambda x: str(x))[-1]
    print(f"Using column: {latest_q}")

    # Filter for England+Wales national stats (or local authority level)
    # Try to find rows with local authority codes (E14 prefix = LA)
    results = []
    for _, row in df.iterrows():
        # Look for LA codes in any column
        code = None
        name = None
        rent_val = None

        for col in cols:
            val = str(row.get(col, '')).strip()
            # ONS LA codes are E14/E05 etc.
            if val.startswith('E14') or val.startswith('E05') or val.startswith('W06'):
                code = val
            if col in ('Area name', 'Local authority name', 'LANAME'):
                name = val
            if str(col) == latest_q:
                try:
                    rent_val = float(val)
                except (ValueError, TypeError):
                    rent_val = None

        if code and name and rent_val and rent_val > 0:
            results.append({
                'code': code,
                'name': name,
                'region': 'unknown',  # Will need LA code → region mapping
                'rent_2br': round(rent_val * 1.15),  # Median 2br ≈ median 1br × 1.15 (rough)
                'ct_band': 'C',
                'ct_annual': 1700,  # Default
                'source': 'ONS PRMS',
                'quarter': str(latest_q),
            })

    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fetch ONS rental data')
    parser.add_argument('--output', '-o', type=Path,
                        default=Path(__file__).parent.parent / 'data' / 'areas.json')
    args = parser.parse_args()

    df = fetch_ons_data(URL_QUARTERLY)
    if df.empty:
        print("Failed to fetch ONS data. Check your internet connection.")
        sys.exit(1)

    areas = extract_areas(df)
    print(f"Extracted {len(areas)} areas from ONS data")

    if not areas:
        print("Warning: no areas extracted. Writing empty list.")
        areas = []

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w') as f:
        json.dump(areas, f, indent=2, ensure_ascii=False)

    print(f"Written {len(areas)} areas to {args.output}")


if __name__ == '__main__':
    main()
