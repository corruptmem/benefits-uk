#!/usr/bin/env python3
"""
UK Benefits Calculator — Precomputation Script

Generates the lookup table used by the web app.

For each scenario family, for each area, for each child-count variant:
  - compute disposable income
  - store the result in data/output/lookup.json

Usage:
  python -m compute.compute
"""

import gzip
import json
import math
import os
import sys
from itertools import product
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from areas import get_uk_average, estimate_council_tax_from_rent, estimate_utilities
from benefits import Household, calculate_benefits, calculate_disposable_income
from tax import (calculate_income_tax, calculate_national_insurance,
                 calculate_student_loan_repayment, calculate_commute_costs)


# ─── Constants ────────────────────────────────────────────────────────────────

HOURS_PER_DAY = 8
WEEKS_PER_YEAR = 52

# Disposable income brackets (lower bound, upper bound)
# We want to find configs that round TO a bracket, not fall within it
INCOME_BRACKETS = list(range(0, 26_000, 1_000))  # £0, £1k, £2k, ... £25k

# Standard wage to test (for precomputing scenarios with wages)
DEFAULT_WAGE = 12.00  # £/hour — minimum wage ~£11.44, use £12 as a mid point


# ─── Scenario Families ────────────────────────────────────────────────────────

# Each scenario family is a function that returns a list of Household configs
# to evaluate for a given area.

def scenarios_single_no_disability(area: dict, days: int, commute: str, child_count: int) -> list:
    """Person 1, no disability, varying children."""
    return [
        Household(
            p1_wage=DEFAULT_WAGE if days > 0 else 0.0,
            p1_days=days,
            p1_pip_care=0,
            p1_pip_mobility=0,
            p1_commute=commute if days > 0 else 'none',
            p1_student_loan=0,
            p2_enabled=False,
            kids_none=child_count,
            kids_lower=0,
            kids_higher=0,
            monthly_rent=area['rent_2br'],
            council_tax=area.get('ct_annual', estimate_council_tax_from_rent(area['rent_2br'])),
            utilities=estimate_utilities(),
        )
    ]


def scenarios_couple_no_disability(area: dict, p1_days: int, p2_days: int,
                                   commute: str, child_count: int) -> list:
    """Two parents, no disability."""
    return [
        Household(
            p1_wage=DEFAULT_WAGE if p1_days > 0 else 0.0,
            p1_days=p1_days,
            p1_pip_care=0,
            p1_pip_mobility=0,
            p1_commute=commute if p1_days > 0 else 'none',
            p1_student_loan=0,
            p2_enabled=True,
            p2_wage=DEFAULT_WAGE if p2_days > 0 else 0.0,
            p2_days=p2_days,
            p2_pip_care=0,
            p2_pip_mobility=0,
            p2_commute=commute if p2_days > 0 else 'none',
            p2_student_loan=0,
            kids_none=child_count,
            kids_lower=0,
            kids_higher=0,
            monthly_rent=area['rent_2br'],
            council_tax=area.get('ct_annual', estimate_council_tax_from_rent(area['rent_2br'])),
            utilities=estimate_utilities(),
        )
    ]


def scenarios_couple_disability(area: dict, p1_days: int, p2_days: int,
                                p1_care: int, p1_mobility: int,
                                p2_care: int, p2_mobility: int,
                                commute: str,
                                child_count: int) -> list:
    """Two parents, both with disability."""
    return [
        Household(
            p1_wage=DEFAULT_WAGE if p1_days > 0 else 0.0,
            p1_days=p1_days,
            p1_pip_care=p1_care,
            p1_pip_mobility=p1_mobility,
            p1_commute=commute if p1_days > 0 else 'none',
            p1_student_loan=0,
            p2_enabled=True,
            p2_wage=DEFAULT_WAGE if p2_days > 0 else 0.0,
            p2_days=p2_days,
            p2_pip_care=p2_care,
            p2_pip_mobility=p2_mobility,
            p2_commute=commute if p2_days > 0 else 'none',
            p2_student_loan=0,
            kids_none=child_count,
            kids_lower=0,
            kids_higher=0,
            monthly_rent=area['rent_2br'],
            council_tax=area.get('ct_annual', estimate_council_tax_from_rent(area['rent_2br'])),
            utilities=estimate_utilities(),
        )
    ]


def scenarios_single_disability(area: dict, days: int,
                                 p1_care: int, p1_mobility: int,
                                 commute: str,
                                 child_count: int) -> list:
    """Person 1 with disability, varying children."""
    return [
        Household(
            p1_wage=DEFAULT_WAGE if days > 0 else 0.0,
            p1_days=days,
            p1_pip_care=p1_care,
            p1_pip_mobility=p1_mobility,
            p1_commute=commute if days > 0 else 'none',
            p1_student_loan=0,
            p2_enabled=False,
            kids_none=child_count,
            kids_lower=0,
            kids_higher=0,
            monthly_rent=area['rent_2br'],
            council_tax=area.get('ct_annual', estimate_council_tax_from_rent(area['rent_2br'])),
            utilities=estimate_utilities(),
        )
    ]


def scenarios_with_children_disability(area: dict,
                                       p1_days: int, p2_days: int,
                                       p1_care: int, p1_mobility: int,
                                       p2_care: int, p2_mobility: int,
                                       commute: str,
                                       kids_none: int,
                                       kids_lower: int,
                                       kids_higher: int) -> list:
    """Two parents, both with disability, varying children across all DLA tiers."""
    return [
        Household(
            p1_wage=DEFAULT_WAGE if p1_days > 0 else 0.0,
            p1_days=p1_days,
            p1_pip_care=p1_care,
            p1_pip_mobility=p1_mobility,
            p1_commute=commute if p1_days > 0 else 'none',
            p1_student_loan=0,
            p2_enabled=True,
            p2_wage=DEFAULT_WAGE if p2_days > 0 else 0.0,
            p2_days=p2_days,
            p2_pip_care=p2_care,
            p2_pip_mobility=p2_mobility,
            p2_commute=commute if p2_days > 0 else 'none',
            p2_student_loan=0,
            kids_none=kids_none,
            kids_lower=kids_lower,
            kids_higher=kids_higher,
            monthly_rent=area['rent_2br'],
            council_tax=area.get('ct_annual', estimate_council_tax_from_rent(area['rent_2br'])),
            utilities=estimate_utilities(),
        )
    ]


# ─── Core Calculation ─────────────────────────────────────────────────────────

def compute_disposable(household: Household) -> tuple[float, dict]:
    """Compute gross income and disposable income for a household."""
    hours_per_day = HOURS_PER_DAY
    gross1 = household.p1_wage * household.p1_days * hours_per_day * WEEKS_PER_YEAR
    gross2 = (household.p2_wage * household.p2_days * hours_per_day * WEEKS_PER_YEAR
              if household.p2_enabled else 0.0)
    total_gross = gross1 + gross2

    income_tax = calculate_income_tax(gross1) + calculate_income_tax(gross2)
    ni = calculate_national_insurance(gross1) + calculate_national_insurance(gross2)

    student_loan = (
        calculate_student_loan_repayment(gross1, household.p1_student_loan) +
        calculate_student_loan_repayment(gross2, household.p2_student_loan)
    )

    p1_commute_cost = calculate_commute_costs(
        household.p1_days, household.p1_commute,
        household.monthly_rent,
        has_pip_mobility_higher=(household.p1_pip_mobility == 2)
    ) if household.p1_commute != 'none' and household.p1_days > 0 else 0.0

    p2_commute_cost = (
        calculate_commute_costs(
            household.p2_days, household.p2_commute,
            household.monthly_rent,
            has_pip_mobility_higher=(household.p2_pip_mobility == 2)
        ) if household.p2_enabled and household.p2_commute != 'none' and household.p2_days > 0 else 0.0
    )

    commute_annual = p1_commute_cost + p2_commute_cost

    return calculate_disposable_income(
        household, total_gross, income_tax, ni, student_loan, commute_annual
    )


def bracket_key(disposable: float) -> str:
    """Map a disposable income to its £1k bracket key."""
    bracket = int(disposable // 1000) * 1000
    return f"{bracket}-{bracket + 1000}"


# ─── Precomputation ───────────────────────────────────────────────────────────

def precompute(areas: list, output_file: Path, min_kids: int = 0, max_kids: int = 7):
    """
    Precompute disposable incomes for all scenario families across all areas.

    Returns a dict: {area_code: {scenario_key: {bracket: {config: ..., disposable: ..., breakdown: ...}}}}
    """
    print(f"Precomputing for {len(areas)} areas, {min_kids}-{max_kids} children...")

    results = {}

    for i, area in enumerate(areas):
        area_code = area.get('code', area.get('name', f'area_{i}'))
        if i % 500 == 0:
            print(f"  [{i}/{len(areas)}] {area['name']}")

        area_results = {}

        # ── Single, no disability ─────────────────────────────────────────────
        for days in [0, 2, 5]:
            commute = 'none' if days == 0 else 'train'
            for kids in range(min_kids, max_kids + 1):
                for h in scenarios_single_no_disability(area, days, commute, kids):
                    disposable, breakdown = compute_disposable(h)
                    bk = bracket_key(disposable)
                    scenario_key = f"single_nd_d{days}_k{kids}"
                    area_results.setdefault(scenario_key, {})[bk] = {
                        'disposable': round(disposable, 2),
                        'config': {
                            'days': days,
                            'commute': commute,
                            'kids': kids,
                            'kids_lower': 0,
                            'kids_higher': 0,
                        },
                        'breakdown': {k: round(v, 2) for k, v in breakdown.items()},
                    }

        # ── Couple, no disability ───────────────────────────────────────────
        for p1d, p2d in [(0, 0), (0, 2), (2, 0), (2, 5), (5, 2), (5, 5)]:
            for kids in range(min_kids, max_kids + 1):
                commute = 'train' if (p1d > 0 or p2d > 0) else 'none'
                for h in scenarios_couple_no_disability(area, p1d, p2d, commute, kids):
                    disposable, breakdown = compute_disposable(h)
                    bk = bracket_key(disposable)
                    scenario_key = f"couple_nd_p1d{p1d}_p2d{p2d}_k{kids}"
                    area_results.setdefault(scenario_key, {})[bk] = {
                        'disposable': round(disposable, 2),
                        'config': {
                            'p1_days': p1d,
                            'p2_days': p2d,
                            'commute': commute,
                            'kids': kids,
                            'kids_lower': 0,
                            'kids_higher': 0,
                        },
                        'breakdown': {k: round(v, 2) for k, v in breakdown.items()},
                    }

        # ── Single with disability ─────────────────────────────────────────
        for days in [0, 2, 5]:
            commute = 'none' if days == 0 else 'train'
            for care, mobility in [(1, 0), (1, 1), (2, 0), (2, 2)]:
                # (care_level, mobility_level) — not all combinations make sense
                for kids in range(min_kids, max_kids + 1):
                    for h in scenarios_single_disability(area, days, care, mobility, commute, kids):
                        disposable, breakdown = compute_disposable(h)
                        bk = bracket_key(disposable)
                        scenario_key = f"single_d{care}{mobility}_d{days}_k{kids}"
                        area_results.setdefault(scenario_key, {})[bk] = {
                            'disposable': round(disposable, 2),
                            'config': {
                                'days': days,
                                'pip_care': care,
                                'pip_mobility': mobility,
                                'commute': commute,
                                'kids': kids,
                            },
                            'breakdown': {k: round(v, 2) for k, v in breakdown.items()},
                        }

        # ── Couple with disability (both parents max claim) ─────────────────
        for p1d, p2d in [(0, 0), (0, 2), (2, 5), (5, 2)]:
            commute = 'train' if (p1d > 0 or p2d > 0) else 'none'
            # Both at highest disability claim (care=3, mobility=2)
            for kids in range(min_kids, max_kids + 1):
                for h in scenarios_couple_disability(
                        area, p1d, p2d, 3, 2, 3, 2, commute, kids):
                    disposable, breakdown = compute_disposable(h)
                    bk = bracket_key(disposable)
                    scenario_key = f"couple_d33_p1d{p1d}_p2d{p2d}_k{kids}"
                    area_results.setdefault(scenario_key, {})[bk] = {
                        'disposable': round(disposable, 2),
                        'config': {
                            'p1_days': p1d,
                            'p2_days': p2d,
                            'p1_care': 3,
                            'p1_mobility': 2,
                            'p2_care': 3,
                            'p2_mobility': 2,
                            'commute': commute,
                            'kids': kids,
                        },
                        'breakdown': {k: round(v, 2) for k, v in breakdown.items()},
                    }

        # ── Couple with disability + children at different DLA tiers ────────
        # Only for p1d=2, p2d=0 (key scenario: one works 2 days, one cares)
        for kids_none in range(min_kids, max_kids + 1):
            for kids_lower in range(min_kids, max_kids + 1):
                for kids_higher in range(min_kids, max_kids + 1):
                    if kids_none + kids_lower + kids_higher == 0:
                        continue
                    for h in scenarios_with_children_disability(
                            area, 2, 0, 3, 2, 3, 2, 'train',
                            kids_none, kids_lower, kids_higher):
                        disposable, breakdown = compute_disposable(h)
                        bk = bracket_key(disposable)
                        scenario_key = f"couple_d33_p1d2_p2d0_k{kids_none}_kl{kids_lower}_kh{kids_higher}"
                        area_results.setdefault(scenario_key, {})[bk] = {
                            'disposable': round(disposable, 2),
                            'config': {
                                'p1_days': 2,
                                'p2_days': 0,
                                'kids_none': kids_none,
                                'kids_lower': kids_lower,
                                'kids_higher': kids_higher,
                            },
                            'breakdown': {k: round(v, 2) for k, v in breakdown.items()},
                        }

        results[area_code] = area_results

    return results


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Precompute UK benefits lookup table')
    parser.add_argument('--output', '-o', type=Path, default=Path('data/output/lookup.json'))
    parser.add_argument('--min-kids', type=int, default=0)
    parser.add_argument('--max-kids', type=int, default=7)
    parser.add_argument('--gzip', action='store_true', help='Output gzip-compressed JSON')
    args = parser.parse_args()

    output_file = args.output
    if args.gzip and output_file.suffix != '.gz':
        output_file = output_file.with_suffix('.json.gz')
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Load areas (or use UK average)
    data_dir = Path(__file__).parent.parent / 'data'
    from areas import load_areas
    areas_data = load_areas(data_dir)

    if areas_data:
        areas = list(areas_data.values())
        print(f"Loaded {len(areas)} areas from data/areas.json")
    else:
        # Fall back to UK average
        uk_avg = get_uk_average()
        areas = [uk_avg]
        print("No areas data found; using UK average only")

    results = precompute(areas, output_file,
                         min_kids=args.min_kids, max_kids=args.max_kids)

    # Write output
    output_file.parent.mkdir(parents=True, exist_ok=True)

    if args.gzip:
        with gzip.open(output_file, 'wt', encoding='utf-8') as f:
            json.dump(results, f)
        print(f"\nWritten gzip-compressed to {output_file}")
    else:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\nWritten to {output_file}")

    # Stats
    total = sum(len(v) for v in results.values())
    print(f"Total scenario × area combinations: {total:,}")


if __name__ == '__main__':
    main()
