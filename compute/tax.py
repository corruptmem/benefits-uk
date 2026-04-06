"""
UK Income Tax, National Insurance, and Student Loan calculation.

Rates for 2024/25 tax year.
"""

from typing import Optional


# ─── Income Tax Bands 2024/25 ────────────────────────────────────────────────

PERSONAL_ALLOWANCE = 12_570
BASIC_RATE_LIMIT = 37_700
HIGHER_RATE_LIMIT = 125_140

BASIC_RATE = 0.20
HIGHER_RATE = 0.40
ADDITIONAL_RATE = 0.45

# Marriage allowance (not modelled in v1)
# MARRIAGE_ALLOWANCE = 1_260

# ─── National Insurance Rates 2024/25 ───────────────────────────────────────

NI_PRIMARY_THRESHOLD = 12_570   # Weekly: £242
NI_UPPER_EARNINGS_LIMIT = 50_270  # Weekly: £967

NI_MAIN_RATE = 0.08   # Between LPL and UEL
NI_ADDITIONAL_RATE = 0.02  # Above UEL


def calculate_income_tax(gross: float, personal_allowance: float = PERSONAL_ALLOWANCE) -> float:
    """
    Calculate annual income tax for a single person.
    Uses UK progressive tax bands.

    Personal Allowance is tapered above £100k (£1 for every £2 above £100k).
    Not modelling this in v1.
    """
    if gross <= personal_allowance:
        return 0.0

    taxable = gross - personal_allowance

    tax = 0.0
    if taxable <= BASIC_RATE_LIMIT:
        tax = taxable * BASIC_RATE
    elif taxable <= HIGHER_RATE_LIMIT:
        tax = BASIC_RATE_LIMIT * BASIC_RATE
        tax += (taxable - BASIC_RATE_LIMIT) * HIGHER_RATE
    else:
        tax = BASIC_RATE_LIMIT * BASIC_RATE
        tax += (HIGHER_RATE_LIMIT - BASIC_RATE_LIMIT) * HIGHER_RATE
        tax += (taxable - HIGHER_RATE_LIMIT) * ADDITIONAL_RATE

    return tax


def calculate_national_insurance(gross: float) -> float:
    """
    Calculate annual employee National Insurance contributions.
    UK 2024/25 rates.
    """
    if gross <= NI_PRIMARY_THRESHOLD:
        return 0.0

    ni = 0.0

    # Between LPL and UEL: 8%
    upper_point = min(gross, NI_UPPER_EARNINGS_LIMIT)
    if upper_point > NI_PRIMARY_THRESHOLD:
        ni += (upper_point - NI_PRIMARY_THRESHOLD) * NI_MAIN_RATE

    # Above UEL: 2%
    if gross > NI_UPPER_EARNINGS_LIMIT:
        ni += (gross - NI_UPPER_EARNINGS_LIMIT) * NI_ADDITIONAL_RATE

    return ni


def calculate_student_loan_repayment(gross: float, plan: int) -> float:
    """
    Calculate annual student loan repayment.

    Plan: 0=none, 1=Plan1, 2=Plan2, 4=Plan4
    """
    if plan == 0:
        return 0.0

    thresholds = {
        1: 25_000,   # Plan 1
        2: 27_295,   # Plan 2
        4: 31_395,   # Plan 4
    }

    threshold = thresholds.get(plan, 0)
    if threshold == 0:
        return 0.0

    repayment_rate = 0.09  # 9% for all plans

    if gross <= threshold:
        return 0.0

    return (gross - threshold) * repayment_rate


def calculate_commute_costs(days_per_week: int,
                            commute_method: str,
                            monthly_rent: float,
                            has_pip_mobility_higher: bool = False) -> float:
    """
    Calculate annual commute costs.

    days_per_week: 0, 2, or 5
    commute_method: 'none', 'car', 'train'
    has_pip_mobility_higher: if True, Motability scheme reduces car costs to £0

    Car costs:
    - AA running costs estimate: ~£2,000/year if Motability (pip_mobility=higher)
      Actually Motability is £0 cost to the user (the car is the benefit)
    - Without Motability: AA estimates ~£2,020/year for a small car
      https://www.theaa.com/posts/the-cost-of-owning-a-car-2023
    - Motability: £0 user cost for PIP high-rate mobility recipients

    Train costs:
    - Uses a "average UK season ticket" approach
    - For 2 days/week: 2-day season ticket premium vs 5-day
    - Average season ticket for UK: ~£3,000-£4,000/year (regional variation)
    - Using £3,500 as a reasonable average for precomputed lookup
    - With Disabled Persons Railcard (£20/year): saves ~1/3 on standard tickets
      Using £2,300 as the discounted 2-day estimate for precomputation
    """
    if days_per_week == 0 or commute_method == 'none':
        return 0.0

    if commute_method == 'car':
        if has_pip_mobility_higher:
            # Motability: user pays nothing for the car itself
            # But there are still costs... actually for simplicity, assume £0
            return 0.0
        else:
            # AA running costs: ~£2,020/year for a small car
            return 2_020.0

    elif commute_method == 'train':
        if days_per_week <= 2:
            # 2-day season ticket with Disabled Persons Railcard (~£2,300/year avg)
            # If no disability: full price ~£3,500/year
            # In precomputation, assume railcard eligibility (simpler model)
            return 2_300.0
        else:
            # 5-day season ticket: ~£4,500/year avg UK
            return 4_500.0

    return 0.0
