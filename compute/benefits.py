"""
UK Benefits Calculation Engine

Calculates entitlement to:
- Universal Credit (UC)
- Personal Independence Payment (PIP)
- Disability Living Allowance for children (DLA child)
- Carer's Allowance
- Child Benefit
- Working Tax Credit / Child Tax Credit (legacy)
"""

from dataclasses import dataclass
from typing import Optional


# ─── 2024/25 Benefit Rates (annual unless stated) ───────────────────────────

# Universal Credit standard allowances (monthly)
UC_SINGLE_UPPER = 473.35  # Single, under 25
UC_SINGLE_LOWER = 617.60  # Single, 25+
UC_COUPLE_UPPER = 743.78  # Couple, both under 25
UC_COUPLE_LOWER = 971.80  # Couple, at least one 25+

# UC work allowances (month, deducted from UC before means-test)
UC_WORK_ALLOWANCE_LCWRA = 673.00  # If has limited capability for work-related activity
UC_WORK_ALLOWANCE_STANDARD = 404.00  # Standard

# UC child elements (monthly per child)
UC_CHILD_ELEMENT = 333.33  # First child (post-April 2017)
UC_CHILD_ELEMENT_SUBSEQUENT = 287.92  # Second+ child
UC_DISABLED_CHILD_ELEMENT_LOWER = 426.37
UC_DISABLED_CHILD_ELEMENT_HIGHER = 809.40

# UC disabled/addition elements (monthly)
UC_DISABILITY_ELEMENT_LCWRA = 421.76  # Limited capability for work-related activity
UC_SEVERE_DISABILITY_ELEMENT = 169.11  # If gets PIP middle/high daily living

# PIP rates (weekly)
PIP_CARE_LOWER = 72.90
PIP_CARE_MIDDLE = 184.30
PIP_CARE_HIGHER = 292.40

PIP_MOBILITY_LOWER = 26.90
PIP_MOBILITY_HIGHER = 71.00

# DLA Child rates (weekly)
DLA_CHILD_CARE_LOWER = 72.90
DLA_CHILD_CARE_MIDDLE = 184.30
DLA_CHILD_CARE_HIGHER = 292.40

DLA_CHILD_MOBILITY_LOWER = 26.90
DLA_CHILD_MOBILITY_HIGHER = 71.00

# Carer's Allowance (weekly)
CARERS_ALLOWANCE = 76.75  # £76.75/week = £3,991/year

# Child Benefit (weekly)
CHILD_BENEFIT_FIRST = 25.60
CHILD_BENEFIT_SUBSEQUENT = 16.95

# Benefit cap (annual, outside London)
BENEFIT_CAP_COUPLE = 25_000.0
BENEFIT_CAP_SINGLE = 16_000.0

# 16-hour threshold (per person per week)
HOURS_16 = 16


@dataclass
class Household:
    """Household configuration."""
    # Person 1
    p1_wage: float          # hourly wage (£)
    p1_days: int            # days worked per week (0, 2, or 5)
    p1_pip_care: int       # 0=none, 1=lower, 2=middle, 3=higher
    p1_pip_mobility: int    # 0=none, 1=lower, 2=higher
    p1_commute: str         # 'none', 'car', 'train'
    p1_student_loan: int    # 0=none, 1=plan1, 2=plan2, 4=plan4

    # Person 2 (optional)
    p2_enabled: bool = False
    p2_wage: float = 0.0
    p2_days: int = 0
    p2_pip_care: int = 0
    p2_pip_mobility: int = 0
    p2_commute: str = 'none'
    p2_student_loan: int = 0

    # Children
    kids_none: int = 0
    kids_lower: int = 0    # lower-rate disabled children
    kids_higher: int = 0  # higher-rate disabled children

    # Location
    monthly_rent: float = 0.0       # PCM
    council_tax: float = 0.0         # annual
    utilities: float = 0.0           # annual


def _pip_weekly(pip_care: int, pip_mobility: int) -> float:
    """Total weekly PIP amount."""
    care = [0, PIP_CARE_LOWER, PIP_CARE_MIDDLE, PIP_CARE_HIGHER][pip_care]
    mobility = [0, PIP_MOBILITY_LOWER, PIP_MOBILITY_HIGHER][pip_mobility]
    return care + mobility


def _dla_child_weekly(kids_lower: int, kids_higher: int) -> float:
    """Total weekly DLA for children."""
    total = 0.0
    total += kids_lower * (DLA_CHILD_CARE_LOWER + DLA_CHILD_MOBILITY_LOWER)
    total += kids_higher * (DLA_CHILD_CARE_HIGHER + DLA_CHILD_MOBILITY_HIGHER)
    return total


def _carers_allowance_entitled(p1_care: int, p1_mobility: int,
                                p2_care: int, p2_mobility: int,
                                p1_days: int, p2_days: int) -> tuple[bool, int]:
    """
    Returns (entitled, carer_person) where carer_person is 1 or 2.
    One person qualifies if they have at least middle-rate daily living PIP
    and the other provides 35+ hours/week of care.
    """
    # Check if Person 1 qualifies as cared-for (middle/high daily living)
    p1_cared_for = p1_care >= 2  # middle or higher daily living

    # Check if Person 2 is the carer (works 0 days / <16h, caring for p1)
    if p1_cared_for and p2_days == 0 and p2_care >= 2:
        return True, 2

    # Check if Person 2 qualifies as cared-for and Person 1 is carer
    p2_cared_for = p2_care >= 2
    if p2_cared_for and p1_days == 0 and p1_care >= 2:
        return True, 1

    return False, 0


def _benefit_cap_applies(total_benefits: float, p1_care: int, p2_care: int,
                          kids_lower: int, kids_higher: int, is_couple: bool) -> bool:
    """
    Returns True if benefit cap applies.
    Cap is lifted if:
    - Either adult has LCWRA (implied by pip_care >= 2, which is middle/high daily living)
    - Any child gets DLA higher rate
    """
    has_lcwra = p1_care >= 2 or (is_couple and p2_care >= 2)
    has_disabled_child = kids_higher > 0
    return not (has_lcwra or has_disabled_child)


def calculate_uc(p1_wage: float, p1_days: int,
                  p2_wage: float, p2_days: int,
                  p1_pip_care: int, p2_pip_care: int,
                  kids_none: int, kids_lower: int, kids_higher: int,
                  p1_lcwra: bool, p2_lcwra: bool) -> tuple[float, float]:
    """
    Calculate Universal Credit entitlement and UC deduction from earnings.

    Returns (uc_entitlement, uc_reduction_from_earnings).
    uc_reduction is the amount subtracted from gross income as UC is phased out.

    Actual take-home: UC - reduction_from_earnings (so net UC = entitlement - reduction)
    Or equivalently: UC_max - earnings_effect, where earnings_effect = min(entitlement, taper_rate × (gross - allowances))

    Standard taper: 55p per £1 earned above work allowance (55% effective marginal rate)
    """
    is_couple = p2_wage > 0 or p2_days > 0

    # Standard allowance (annual)
    if is_couple:
        uc_max = UC_COUPLE_LOWER * 12
    else:
        uc_max = UC_SINGLE_LOWER * 12

    # Work allowances (monthly)
    if is_couple:
        # Both can have LCWRA — use the higher allowance
        if p1_lcwra and p2_lcwra:
            wa1 = UC_WORK_ALLOWANCE_LCWRA
            wa2 = UC_WORK_ALLOWANCE_LCWRA
        elif p1_lcwra:
            wa1 = UC_WORK_ALLOWANCE_LCWRA
            wa2 = UC_WORK_ALLOWANCE_STANDARD
        elif p2_lcwra:
            wa1 = UC_WORK_ALLOWANCE_STANDARD
            wa2 = UC_WORK_ALLOWANCE_LCWRA
        else:
            wa1 = UC_WORK_ALLOWANCE_STANDARD
            wa2 = UC_WORK_ALLOWANCE_STANDARD
    else:
        wa1 = UC_WORK_ALLOWANCE_LCWRA if p1_lcwra else UC_WORK_ALLOWANCE_STANDARD
        wa2 = 0.0

    # Child elements (monthly)
    child_elements_monthly = 0.0
    if kids_none > 0:
        child_elements_monthly += UC_CHILD_ELEMENT
        if kids_none > 1:
            child_elements_monthly += (kids_none - 1) * UC_CHILD_ELEMENT_SUBSEQUENT
    if kids_lower > 0:
        child_elements_monthly += kids_lower * UC_DISABLED_CHILD_ELEMENT_LOWER
    if kids_higher > 0:
        child_elements_monthly += kids_higher * UC_DISABLED_CHILD_ELEMENT_HIGHER

    # Disabled/addition elements (monthly)
    disability_elements_monthly = 0.0
    if p1_lcwra or p1_pip_care >= 2:
        disability_elements_monthly += UC_SEVERE_DISABILITY_ELEMENT
    if is_couple and (p2_lcwra or p2_pip_care >= 2):
        disability_elements_monthly += UC_SEVERE_DISABILITY_ELEMENT

    # Total UC maximum (annual)
    uc_max += (child_elements_monthly + disability_elements_monthly) * 12

    # Gross annual earnings
    hours_per_day = 8
    gross1 = p1_wage * p1_days * hours_per_day * 52
    gross2 = p2_wage * p2_days * hours_per_day * 52 if is_couple else 0.0
    total_gross = gross1 + gross2

    # Earnings above work allowances (monthly)
    net_wa = (max(0, (gross1 / 12) - wa1) +
               max(0, (gross2 / 12) - wa2))

    # Taper: 55% of earnings above allowance
    # UC reduced by 55p per £1 earned above allowance
    monthly_taper = net_wa * 0.55
    uc_entitlement = max(0, uc_max / 12 - monthly_taper) * 12  # annual

    return uc_entitlement / 12 * 12, uc_entitlement  # returns (monthly, annual) — simplify


def calculate_benefits(household: Household) -> dict:
    """
    Calculate all benefit entitlements for a household configuration.
    Returns a dict with breakdown.
    """
    is_couple = household.p2_enabled

    # ── PIP ─────────────────────────────────────────────────────────────────
    p1_pip_weekly = _pip_weekly(household.p1_pip_care, household.p1_pip_mobility)
    p2_pip_weekly = _pip_weekly(household.p2_pip_care, household.p2_pip_mobility) if is_couple else 0.0

    # LCWRA (Limited Capability for Work-Related Activity) — triggered by
    # receiving the middle or higher rate of the daily living component of PIP
    p1_lcwra = household.p1_pip_care >= 2
    p2_lcwra = household.p2_pip_care >= 2 if is_couple else False

    # ── DLA Child ──────────────────────────────────────────────────────────
    dla_child_weekly = _dla_child_weekly(household.kids_lower, household.kids_higher)
    dla_child_annual = dla_child_weekly * 52

    # ── Carer's Allowance ─────────────────────────────────────────────────
    carers_allowance_annual = 0.0
    if is_couple:
        entitled, _ = _carers_allowance_entitled(
            household.p1_pip_care, household.p1_pip_mobility,
            household.p2_pip_care, household.p2_pip_mobility,
            household.p1_days, household.p2_days
        )
        if entitled:
            carers_allowance_annual = CARERS_ALLOWANCE * 52

    # ── Universal Credit ───────────────────────────────────────────────────
    # UC is means-tested; we need gross income to calculate it
    hours_per_day = 8
    gross1 = household.p1_wage * household.p1_days * hours_per_day * 52
    gross2 = (household.p2_wage * household.p2_days * hours_per_day * 52) if is_couple else 0.0
    total_gross = gross1 + gross2

    # UC maximum (annual)
    if is_couple:
        uc_max_monthly = UC_COUPLE_LOWER
    else:
        uc_max_monthly = UC_SINGLE_LOWER

    # Child elements
    child_elem_monthly = 0.0
    if household.kids_none > 0:
        child_elem_monthly += UC_CHILD_ELEMENT
        if household.kids_none > 1:
            child_elem_monthly += (household.kids_none - 1) * UC_CHILD_ELEMENT_SUBSEQUENT
    if household.kids_lower > 0:
        child_elem_monthly += household.kids_lower * UC_DISABLED_CHILD_ELEMENT_LOWER
    if household.kids_higher > 0:
        child_elem_monthly += household.kids_higher * UC_DISABLED_CHILD_ELEMENT_HIGHER

    # Disabled additions
    disability_elem_monthly = 0.0
    if p1_lcwra:
        disability_elem_monthly += UC_SEVERE_DISABILITY_ELEMENT
    if is_couple and p2_lcwra:
        disability_elem_monthly += UC_SEVERE_DISABILITY_ELEMENT

    uc_max_annual = (uc_max_monthly + child_elem_monthly + disability_elem_monthly) * 12

    # Work allowances (monthly)
    if is_couple:
        wa1 = UC_WORK_ALLOWANCE_LCWRA if p1_lcwra else UC_WORK_ALLOWANCE_STANDARD
        wa2 = UC_WORK_ALLOWANCE_LCWRA if p2_lcwra else UC_WORK_ALLOWANCE_STANDARD
    else:
        wa1 = UC_WORK_ALLOWANCE_LCWRA if p1_lcwra else UC_WORK_ALLOWANCE_STANDARD
        wa2 = 0.0

    # Earnings above allowance (monthly)
    gross1_monthly = gross1 / 12
    gross2_monthly = gross2 / 12
    earn_above_wa = max(0, gross1_monthly - wa1) + max(0, gross2_monthly - wa2)

    # UC taper: 55p per £1 earned above allowance
    monthly_taper = earn_above_wa * 0.55
    uc_monthly = max(0, uc_max_monthly + child_elem_monthly + disability_elem_monthly - monthly_taper)
    uc_annual = uc_monthly * 12

    # ── Child Benefit ───────────────────────────────────────────────────────
    # withdrawn at £60k/yr single income, £100k joint — simplified (not modelling HITC in v1)
    cb_weekly = CHILD_BENEFIT_FIRST + max(0, (household.kids_none + household.kids_lower + household.kids_higher - 1)) * CHILD_BENEFIT_SUBSEQUENT
    child_benefit_annual = cb_weekly * 52

    # ── Total Benefits ─────────────────────────────────────────────────────
    total_benefits_annual = (
        p1_pip_weekly * 52 +
        p2_pip_weekly * 52 +
        dla_child_annual +
        carers_allowance_annual +
        uc_annual +
        child_benefit_annual
    )

    # ── Benefit Cap ────────────────────────────────────────────────────────
    cap = BENEFIT_CAP_COUPLE if is_couple else BENEFIT_CAP_SINGLE
    cap_lifted = p1_lcwra or (is_couple and p2_lcwra) or household.kids_higher > 0

    benefits_before_cap = total_benefits_annual
    if cap_lifted:
        cap_deduction = 0.0
    else:
        cap_deduction = max(0, benefits_before_cap - cap)

    total_benefits_after_cap = benefits_before_cap - cap_deduction

    # UC element of cap deduction
    # (Carer's Allowance also counts toward cap, PIP/DLA child do not)
    uc_in_cap = min(uc_annual, max(0, cap - (p1_pip_weekly * 52 + p2_pip_weekly * 52 + dla_child_annual + carers_allowance_annual)))

    return {
        'pip_p1_annual': p1_pip_weekly * 52,
        'pip_p2_annual': p2_pip_weekly * 52,
        'dla_child_annual': dla_child_annual,
        'carers_allowance_annual': carers_allowance_annual,
        'uc_annual': uc_annual,
        'child_benefit_annual': child_benefit_annual,
        'total_benefits_before_cap': benefits_before_cap,
        'cap_applied': cap_deduction,
        'cap_lifted': cap_lifted,
        'total_benefits': total_benefits_after_cap,
        'p1_lcwra': p1_lcwra,
        'p2_lcwra': p2_lcwra if is_couple else False,
        'uc_in_cap': uc_in_cap,
    }


def calculate_disposable_income(household: Household,
                                 gross_annual: float,
                                 income_tax_annual: float,
                                 ni_annual: float,
                                 student_loan_annual: float,
                                 commute_annual: float) -> tuple[float, dict]:
    """
    Calculate disposable income given household config and deductions.

    Returns (disposable_income_annual, breakdown_dict)
    """
    benefits = calculate_benefits(household)

    costs_annual = (
        household.monthly_rent * 12 +
        household.council_tax +
        household.utilities +
        commute_annual
    )

    disposable = (
        gross_annual +
        benefits['total_benefits'] -
        income_tax_annual -
        ni_annual -
        student_loan_annual -
        costs_annual
    )

    breakdown = {
        'gross_income': gross_annual,
        'income_tax': income_tax_annual,
        'national_insurance': ni_annual,
        'student_loan': student_loan_annual,
        'benefits_total': benefits['total_benefits'],
        'rent': household.monthly_rent * 12,
        'council_tax': household.council_tax,
        'utilities': household.utilities,
        'transport': commute_annual,
        'total_costs': costs_annual,
        'disposable_income': disposable,
        **benefits,
    }

    return disposable, breakdown
