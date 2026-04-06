/**
 * UK Benefits Calculator — Client-side calculation engine + UI
 *
 * Replicates the Python benefits.py + tax.py logic in JS.
 * All calculations run entirely in the browser — no data sent anywhere.
 */

// ─── Constants ────────────────────────────────────────────────────────────────

const HOURS_PER_DAY = 8;
const WEEKS_PER_YEAR = 52;

// PIP rates (weekly)
const PIP_CARE = [0, 72.90, 184.30, 292.40];   // [none, lower, middle, higher]
const PIP_MOBILITY = [0, 26.90, 71.00];          // [none, lower, higher]

// DLA Child rates (weekly)
const DLA_CARE = [0, 72.90, 184.30, 292.40];
const DLA_MOBILITY = [0, 26.90, 71.00];

// UC rates (monthly)
const UC_SINGLE_LOWER = 617.60;
const UC_COUPLE_LOWER = 971.80;
const UC_WORK_ALLOWANCE_LCWRA = 673.00;
const UC_WORK_ALLOWANCE_STANDARD = 404.00;
const UC_CHILD_ELEMENT = 333.33;
const UC_CHILD_ELEMENT_SUBSEQUENT = 287.92;
const UC_DISABLED_CHILD_LOWER = 426.37;
const UC_DISABLED_CHILD_HIGHER = 809.40;
const UC_SEVERE_DISABILITY = 169.11;

// Carer's Allowance (£/week)
const CARERS_ALLOWANCE = 76.75;

// Child Benefit (£/week)
const CHILD_BENEFIT_FIRST = 25.60;
const CHILD_BENEFIT_SUBSEQUENT = 16.95;

// Benefit cap (annual)
const BENEFIT_CAP_COUPLE = 25_000;
const BENEFIT_CAP_SINGLE = 16_000;

// Income tax bands (2024/25)
const PA = 12_570;
const BASIC_RATE_LIMIT = 37_700;
const HIGHER_RATE_LIMIT = 125_140;
const BASIC_RATE = 0.20;
const HIGHER_RATE = 0.40;
const ADDITIONAL_RATE = 0.45;

// NI thresholds (2024/25)
const NI_LPL = 12_570;
const NI_UEL = 50_270;
const NI_MAIN_RATE = 0.08;
const NI_ADDITIONAL_RATE = 0.02;

// Student loan thresholds
const SL_THRESHOLDS = { 1: 25_000, 2: 27_295, 4: 31_395 };
const SL_RATE = 0.09;

// Commute costs (£/year)
const CAR_COST_NO_MOTABILITY = 2_020;
const TRAIN_COST_2DAY = 2_300;
const TRAIN_COST_5DAY = 4_500;


// ─── Calculation Functions ──────────────────────────────────────────────────────

function calcIncomeTax(gross) {
  if (gross <= PA) return 0;
  let tax = 0;
  const taxable = gross - PA;
  if (taxable <= BASIC_RATE_LIMIT) {
    tax = taxable * BASIC_RATE;
  } else if (taxable <= HIGHER_RATE_LIMIT) {
    tax = BASIC_RATE_LIMIT * BASIC_RATE;
    tax += (taxable - BASIC_RATE_LIMIT) * HIGHER_RATE;
  } else {
    tax = BASIC_RATE_LIMIT * BASIC_RATE;
    tax += (HIGHER_RATE_LIMIT - BASIC_RATE_LIMIT) * HIGHER_RATE;
    tax += (taxable - HIGHER_RATE_LIMIT) * ADDITIONAL_RATE;
  }
  return tax;
}

function calcNI(gross) {
  if (gross <= NI_LPL) return 0;
  let ni = 0;
  const upperPoint = Math.min(gross, NI_UEL);
  if (upperPoint > NI_LPL) {
    ni += (upperPoint - NI_LPL) * NI_MAIN_RATE;
  }
  if (gross > NI_UEL) {
    ni += (gross - NI_UEL) * NI_ADDITIONAL_RATE;
  }
  return ni;
}

function calcStudentLoan(gross, plan) {
  if (!plan || plan === 0) return 0;
  const threshold = SL_THRESHOLDS[plan] || 0;
  if (!threshold || gross <= threshold) return 0;
  return (gross - threshold) * SL_RATE;
}

function calcCommute(daysPerWeek, method, pipMobilityHigher) {
  if (daysPerWeek === 0 || method === 'none') return 0;
  if (method === 'car') {
    return pipMobilityHigher ? 0 : CAR_COST_NO_MOTABILITY;
  }
  if (method === 'train') {
    return daysPerWeek <= 2 ? TRAIN_COST_2DAY : TRAIN_COST_5DAY;
  }
  return 0;
}

function calcPIP(pipCare, pipMobility) {
  return (PIP_CARE[pipCare] || 0) + (PIP_MOBILITY[pipMobility] || 0);
}

function calcDLAChild(kidsLower, kidsHigher) {
  return kidsLower * (DLA_CARE[1] + DLA_MOBILITY[1]) * 52
       + kidsHigher * (DLA_CARE[3] + DLA_MOBILITY[2]) * 52;
}

function calcBenefits(p1Days, p2Days, p1Care, p2Care,
                      p1Mobility, p2Mobility,
                      kidsNone, kidsLower, kidsHigher,
                      gross1, gross2) {
  const isCouple = p2Days > 0 || p2Care > 0 || p2Mobility > 0;

  const p1PipWeekly = calcPIP(p1Care, p1Mobility);
  const p2PipWeekly = isCouple ? calcPIP(p2Care, p2Mobility) : 0;

  // LCWRA: middle or higher daily living PIP
  const p1LCWRA = p1Care >= 2;
  const p2LCWRA = isCouple && p2Care >= 2;

  const dlaChildAnnual = calcDLAChild(kidsLower, kidsHigher);

  // Carer's Allowance
  let carersAnnual = 0;
  if (isCouple) {
    const p1CaredFor = p1Care >= 2;
    const p2CaredFor = p2Care >= 2;
    if (p1CaredFor && p2Days === 0 && p2Care >= 2) carersAnnual = CARERS_ALLOWANCE * 52;
    else if (p2CaredFor && p1Days === 0 && p1Care >= 2) carersAnnual = CARERS_ALLOWANCE * 52;
  }

  // UC maximum (monthly)
  let ucMaxMonthly = isCouple ? UC_COUPLE_LOWER : UC_SINGLE_LOWER;

  // Child elements
  let childElemMonthly = 0;
  if (kidsNone > 0) {
    childElemMonthly += UC_CHILD_ELEMENT;
    if (kidsNone > 1) childElemMonthly += (kidsNone - 1) * UC_CHILD_ELEMENT_SUBSEQUENT;
  }
  if (kidsLower > 0) childElemMonthly += kidsLower * UC_DISABLED_CHILD_LOWER;
  if (kidsHigher > 0) childElemMonthly += kidsHigher * UC_DISABLED_CHILD_HIGHER;

  // Disability additions
  let disabilityElemMonthly = 0;
  if (p1LCWRA || p1Care >= 2) disabilityElemMonthly += UC_SEVERE_DISABILITY;
  if (isCouple && (p2LCWRA || p2Care >= 2)) disabilityElemMonthly += UC_SEVERE_DISABILITY;

  const ucMaxAnnual = (ucMaxMonthly + childElemMonthly + disabilityElemMonthly) * 12;

  // Work allowances
  const wa1 = p1LCWRA ? UC_WORK_ALLOWANCE_LCWRA : UC_WORK_ALLOWANCE_STANDARD;
  const wa2 = isCouple
    ? (p2LCWRA ? UC_WORK_ALLOWANCE_LCWRA : UC_WORK_ALLOWANCE_STANDARD)
    : 0;

  // Earnings above allowance (monthly)
  const gross1Monthly = gross1 / 12;
  const gross2Monthly = gross2 / 12;
  const earnAboveWa = Math.max(0, gross1Monthly - wa1) + Math.max(0, gross2Monthly - wa2);

  // UC taper: 55p per £1
  const monthlyTaper = earnAboveWa * 0.55;
  const ucMonthly = Math.max(0, ucMaxMonthly + childElemMonthly + disabilityElemMonthly - monthlyTaper);
  const ucAnnual = ucMonthly * 12;

  // Child Benefit
  const totalKids = kidsNone + kidsLower + kidsHigher;
  const cbWeekly = totalKids > 0
    ? CHILD_BENEFIT_FIRST + Math.max(0, totalKids - 1) * CHILD_BENEFIT_SUBSEQUENT
    : 0;

  const pip1Annual = p1PipWeekly * 52;
  const pip2Annual = p2PipWeekly * 52;

  const totalBenefits =
    pip1Annual + pip2Annual + dlaChildAnnual + carersAnnual + ucAnnual + cbWeekly * 52;

  // Benefit cap
  const cap = isCouple ? BENEFIT_CAP_COUPLE : BENEFIT_CAP_SINGLE;
  const capLifted = p1LCWRA || (isCouple && p2LCWRA) || kidsHigher > 0;
  const capDeduction = capLifted ? 0 : Math.max(0, totalBenefits - cap);

  return {
    pip1Annual,
    pip2Annual,
    dlaChildAnnual,
    carersAnnual,
    ucAnnual,
    childBenefitAnnual: cbWeekly * 52,
    totalBenefits: totalBenefits - capDeduction,
    capApplied: capDeduction,
    capLifted,
    p1LCWRA,
    p2LCWRA,
  };
}

function calcDisposable(params) {
  const {
    p1Wage, p1Days, p1Care, p1Mobility, p1Commute, p1Loan,
    p2Enabled, p2Wage, p2Days, p2Care, p2Mobility, p2Commute, p2Loan,
    kidsNone, kidsLower, kidsHigher,
    monthlyRent, councilTax, utilities,
  } = params;

  const gross1 = p1Wage * p1Days * HOURS_PER_DAY * WEEKS_PER_YEAR;
  const gross2 = p2Enabled
    ? p2Wage * p2Days * HOURS_PER_DAY * WEEKS_PER_YEAR
    : 0;
  const totalGross = gross1 + gross2;

  const incomeTax = calcIncomeTax(gross1) + calcIncomeTax(gross2);
  const ni = calcNI(gross1) + calcNI(gross2);
  const studentLoan = calcStudentLoan(gross1, p1Loan) + calcStudentLoan(gross2, p2Loan);

  const p1CommuteCost = calcCommute(p1Days, p1Commute, p1Mobility === 2);
  const p2CommuteCost = p2Enabled ? calcCommute(p2Days, p2Commute, p2Mobility === 2) : 0;
  const commuteTotal = p1CommuteCost + p2CommuteCost;

  const benefits = calcBenefits(
    p1Days, p2Days, p1Care, p2Care, p1Mobility, p2Mobility,
    kidsNone, kidsLower, kidsHigher, gross1, gross2
  );

  const costs = monthlyRent * 12 + councilTax + utilities + commuteTotal;

  const disposable = totalGross + benefits.totalBenefits - incomeTax - ni - studentLoan - costs;

  return {
    grossIncome: totalGross,
    incomeTax,
    nationalInsurance: ni,
    studentLoan,
    ...benefits,
    rent: monthlyRent * 12,
    councilTax,
    utilities,
    transport: commuteTotal,
    totalCosts: costs,
    disposableIncome: disposable,
  };
}

function fmt(n) {
  return '£' + Math.round(n).toLocaleString('en-GB');
}

function fmtMonthly(annual) {
  return '£' + Math.round(annual / 12).toLocaleString('en-GB') + '/mo';
}


// ─── UI ───────────────────────────────────────────────────────────────────────

const state = {
  p1Wage: 12.00,
  p1Days: 0,
  p1Care: 0,
  p1Mobility: 0,
  p1Commute: 'none',
  p1Loan: 0,
  p2Enabled: false,
  p2Wage: 12.00,
  p2Days: 0,
  p2Care: 0,
  p2Mobility: 0,
  p2Commute: 'none',
  p2Loan: 0,
  kidsNone: 0,
  kidsLower: 0,
  kidsHigher: 0,
  monthlyRent: 950,
  councilTax: 1700,
  utilities: 2200,
};

function getState() {
  return {
    ...state,
    p1Wage: parseFloat(document.getElementById('p1-wage').value) || 0,
    p1Days: parseInt(document.querySelector('[data-field="p1-days"].active')?.dataset.value || 0),
    p1Care: parseInt(document.getElementById('p1-pip-care').value) || 0,
    p1Mobility: parseInt(document.getElementById('p1-pip-mobility').value) || 0,
    p1Commute: document.getElementById('p1-commute').value,
    p1Loan: parseInt(document.getElementById('p1-student-loan').value) || 0,
    p2Enabled: document.getElementById('p2-enabled').checked,
    p2Wage: parseFloat(document.getElementById('p2-wage').value) || 0,
    p2Days: parseInt(document.querySelector('[data-field="p2-days"].active')?.dataset.value || 0),
    p2Care: parseInt(document.getElementById('p2-pip-care').value) || 0,
    p2Mobility: parseInt(document.getElementById('p2-pip-mobility').value) || 0,
    p2Commute: document.getElementById('p2-commute').value,
    p2Loan: parseInt(document.getElementById('p2-student-loan').value) || 0,
    kidsNone: state.kidsNone,
    kidsLower: state.kidsLower,
    kidsHigher: state.kidsHigher,
    monthlyRent: parseFloat(document.getElementById('monthly-rent').value) || 0,
    councilTax: parseFloat(document.getElementById('council-tax').value) || 0,
    utilities: parseFloat(document.getElementById('utilities').value) || 0,
  };
}

function showResults(result) {
  const section = document.getElementById('results-section');
  section.style.display = 'block';
  section.scrollIntoView({ behavior: 'smooth', block: 'start' });

  // Hero
  const hero = document.getElementById('disposable-hero');
  const disposable = result.disposableIncome;
  const isNegative = disposable < 0;
  hero.className = 'disposable-hero' + (isNegative ? ' negative' : '');
  hero.innerHTML = `
    <div class="amount">${fmt(disposable)}</div>
    <div class="label">disposable income per year &nbsp;·&nbsp; ${fmtMonthly(disposable)}</div>
  `;

  // Income
  document.getElementById('results-income').innerHTML = `
    <div class="result-rows">
      <div class="result-row income">
        <span class="label">Gross income (wages)</span>
        <span class="amount">${fmt(result.grossIncome)} / ${fmtMonthly(result.grossIncome)}</span>
      </div>
    </div>
  `;

  // Benefits
  const b = result;
  document.getElementById('results-benefits').innerHTML = `
    <div class="result-rows">
      <div class="result-row benefit">
        <span class="label">Universal Credit</span>
        <span class="amount">${fmt(b.ucAnnual)}</span>
      </div>
      ${b.pip1Annual > 0 ? `
      <div class="result-row benefit">
        <span class="label">PIP — Person 1${b.p1LCWRA ? ' (LCWRA)' : ''}</span>
        <span class="amount">${fmt(b.pip1Annual)}</span>
      </div>` : ''}
      ${b.pip2Annual > 0 ? `
      <div class="result-row benefit">
        <span class="label">PIP — Person 2${b.p2LCWRA ? ' (LCWRA)' : ''}</span>
        <span class="amount">${fmt(b.pip2Annual)}</span>
      </div>` : ''}
      ${b.dlaChildAnnual > 0 ? `
      <div class="result-row benefit">
        <span class="label">DLA — Children</span>
        <span class="amount">${fmt(b.dlaChildAnnual)}</span>
      </div>` : ''}
      ${b.carersAnnual > 0 ? `
      <div class="result-row benefit">
        <span class="label">Carer's Allowance</span>
        <span class="amount">${fmt(b.carersAnnual)}</span>
      </div>` : ''}
      ${b.childBenefitAnnual > 0 ? `
      <div class="result-row benefit">
        <span class="label">Child Benefit</span>
        <span class="amount">${fmt(b.childBenefitAnnual)}</span>
      </div>` : ''}
      ${b.capApplied > 0 ? `
      <div class="result-row deduction">
        <span class="label">Benefit cap deduction</span>
        <span class="amount">−${fmt(b.capApplied)}</span>
      </div>` : ''}
      ${b.capLifted ? `
      <div class="result-row benefit">
        <span class="label" style="color:var(--success)">✓ Benefit cap lifted (LCWRA / disabled child)</span>
        <span class="amount"></span>
      </div>` : ''}
      <div class="result-row benefit" style="font-weight:700; border-top:2px solid var(--border)">
        <span class="label">Total benefits</span>
        <span class="amount">${fmt(b.totalBenefits)}</span>
      </div>
    </div>
  `;

  // Deductions
  document.getElementById('results-deductions').innerHTML = `
    <div class="result-rows">
      <div class="result-row deduction">
        <span class="label">Income tax</span>
        <span class="amount">−${fmt(result.incomeTax)}</span>
      </div>
      <div class="result-row deduction">
        <span class="label">National Insurance</span>
        <span class="amount">−${fmt(result.nationalInsurance)}</span>
      </div>
      ${result.studentLoan > 0 ? `
      <div class="result-row deduction">
        <span class="label">Student loan repayment</span>
        <span class="amount">−${fmt(result.studentLoan)}</span>
      </div>` : ''}
    </div>
  `;

  // Costs
  document.getElementById('results-costs').innerHTML = `
    <div class="result-rows">
      <div class="result-row cost">
        <span class="label">Rent (${fmtMonthly(result.rent / 12)})</span>
        <span class="amount">−${fmt(result.rent)}</span>
      </div>
      <div class="result-row cost">
        <span class="label">Council tax</span>
        <span class="amount">−${fmt(result.councilTax)}</span>
      </div>
      <div class="result-row cost">
        <span class="label">Utilities</span>
        <span class="amount">−${fmt(result.utilities)}</span>
      </div>
      ${result.transport > 0 ? `
      <div class="result-row cost">
        <span class="label">Commute costs</span>
        <span class="amount">−${fmt(result.transport)}</span>
      </div>` : ''}
      <div class="result-row cost" style="font-weight:700; border-top:2px solid var(--border)">
        <span class="label">Total costs</span>
        <span class="amount">−${fmt(result.totalCosts)}</span>
      </div>
    </div>
  `;
}


// ─── Event Bindings ────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {

  // Toggle buttons
  document.querySelectorAll('.toggle-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const field = btn.dataset.field;
      const group = document.querySelectorAll(`[data-field="${field}"]`);
      group.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    });
  });

  // Person 2 toggle
  document.getElementById('p2-enabled').addEventListener('change', e => {
    const p2 = document.getElementById('person2');
    if (e.target.checked) {
      p2.style.display = 'block';
      p2.disabled = false;
    } else {
      p2.style.display = 'none';
      p2.disabled = true;
    }
  });

  // Child counters
  const counters = ['kids-none', 'kids-lower', 'kids-higher'];
  counters.forEach(id => {
    const key = id.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
    document.querySelector(`.counter-btn.plus[data-counter="${id}"]`)?.addEventListener('click', () => {
      if (state[key] < 7) { state[key]++; updateCounterDisplay(id); }
    });
    document.querySelector(`.counter-btn.minus[data-counter="${id}"]`)?.addEventListener('click', () => {
      if (state[key] > 0) { state[key]--; updateCounterDisplay(id); }
    });
  });

  function updateCounterDisplay(id) {
    const key = id.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
    const el = document.getElementById(id);
    if (el) el.textContent = state[key];
  }

  // Calculate button
  document.getElementById('calculate-btn').addEventListener('click', () => {
    const params = getState();
    const result = calcDisposable(params);
    showResults(result);
  });

  // Sensitivity: 1 more day
  document.getElementById('sens-1day').addEventListener('click', () => {
    const params = getState();
    params.p1Days = Math.min(5, params.p1Days + 1);
    if (params.p1Commute === 'none' && params.p1Days > 0) params.p1Commute = 'train';
    if (params.p2Enabled) {
      params.p2Days = Math.min(5, params.p2Days + 1);
      if (params.p2Commute === 'none' && params.p2Days > 0) params.p2Commute = 'train';
    }
    showResults(calcDisposable(params));
  });

  // Sensitivity: no kids
  document.getElementById('sens-nokids').addEventListener('click', () => {
    const params = getState();
    params.kidsNone = 0;
    params.kidsLower = 0;
    params.kidsHigher = 0;
    showResults(calcDisposable(params));
  });

  // Sensitivity: no disability claims
  document.getElementById('sens-nodisability').addEventListener('click', () => {
    const params = getState();
    params.p1Care = 0;
    params.p1Mobility = 0;
    params.p2Care = 0;
    params.p2Mobility = 0;
    params.kidsLower = 0;
    params.kidsHigher = 0;
    showResults(calcDisposable(params));
  });

  // Sensitivity: cheapest area (just lower rent to average)
  document.getElementById('sens-cheapestarea').addEventListener('click', () => {
    const params = getState();
    params.monthlyRent = 600;  // roughly the UK cheapest quartile
    params.councilTax = 1000;
    showResults(calcDisposable(params));
  });

});
