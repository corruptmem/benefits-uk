# SPEC.md — UK Benefits & Disposable Income Calculator

## 1. Concept & Vision

A static, privacy-first UK household income calculator that helps people understand how different life configurations — location, working patterns, disability status, children — map to actual disposable income after taxes, housing, transport, and benefits entitlements.

Unlike generic budget calculators, this tool is built around the **inverse problem**: given a desired disposable income bracket, what configuration of area/kids/work/benefits gets you there? It's not trying to sell anything or collect data — just honest numbers.

The tone is matter-of-fact, slightly wonky, and non-judgemental. Zero earning potential is the point: this is a civic tool dressed up as a personal side-project.

---

## 2. Design Language

**Aesthetic direction:** Clean, slightly bureaucratic — like a well-designed government digital service. Not cold or hostile, but honest. Think GOV.UK meets a good actuarial spreadsheet.

**Colour palette:**
- Background: `#f3f2f1` (warm off-white, GOV.UK stone)
- Surface: `#ffffff`
- Primary: `#1d70b8` (GOV.UK blue)
- Success: `#00703c`
- Warning: `#f47738`
- Error: `#d4351c`
- Text: `#0b0c0c`
- Secondary text: `#505a5f`
- Border: `#b1b4b6`
- Highlight: `#ffdd00` (modest HMRC yellow)

**Typography:**
- Headings: `system-ui`, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif
- Body: same stack, lighter weights
- Monospace (numbers/tables): `"Courier New", Courier, monospace`
- No external font dependencies — keeps it fast and offline-friendly

**Spatial system:**
- 8px base unit
- Generous whitespace in results area, dense in input form
- Single-column mobile, two-column desktop for input/output split

**Motion philosophy:**
- Minimal. Only: result panel fades in (200ms ease-out) when calculation completes
- No decorative animation
- Keyboard accessible throughout

**Visual assets:**
- No images or icons beyond basic Unicode/emoji for disability indicators
- Tables for data display, no charts in v1
- Simple inline SVG for the UK outline or region labels if needed

---

## 3. Layout & Structure

```
┌─────────────────────────────────────────┐
│  Header: "UK Benefits Calculator"        │
│  Subline: privacy note, no data leaves  │
├─────────────────────────────────────────┤
│  Step 1: Household                      │
│  [Person 1 income / work / disability]  │
│  [Person 2 income / work / disability]  │
│  [Children counts by disability level]   │
├─────────────────────────────────────────┤
│  Step 2: Location & Costs               │
│  [Select UK area / BUa]                │
│  [Commute method + days]                │
│  [Student loan plan]                    │
├─────────────────────────────────────────┤
│  Step 3: Calculate → Results            │
├─────────────────────────────────────────┤
│  Results panel:                         │
│  - Disposable income estimate           │
│  - Benefits breakdown (UC, PIP, DLA…)  │
│  - Tax/NI/student loan breakdown        │
│  - Rent + council tax + utilities       │
│  - Transport costs                     │
│  - Sensitivity: "what if you worked     │
│    1 more day?" quick calcs            │
└─────────────────────────────────────────┘
```

Responsive: stacks vertically on mobile.

---

## 4. Features & Interactions

### 4.1 Input Form

**Household section:**
- Person 1 (required): hourly wage (£), days worked per week (0/2/5), disability components (care: none/low/middle/high, mobility: none/lower/higher), student loan plan (N/A/Plan 1/Plan 2/Plan 4), commute method (N/A/car/train)
- Person 2 (optional, toggle to enable): same fields, N/A means single parent
- Children: three counters — non-disabled kids, kids with lower-rate disability, kids with higher-rate disability (each 0-7)

**Location section:**
- Searchable dropdown of 7,018 UK Built-Up Areas (ONS)
- Pre-loaded average monthly private rent for 1-bed, 2-bed, 3-bed in that area
- User selects which size property applies
- Auto-fills: council tax band estimate (from area), average utilities

**Commute section:**
- Days worked (derived from Person 1 + Person 2)
- Commute method (car: uses Motability eligibility + AA running costs estimate; train: uses TfNSW/TfL railcard logic + season ticket estimate)
- Car: factors in Motability if high-rate PIP mobility, shows cheaper option

**Student loan:**
- Plan selector per person (N/A means no loan)
- Pre-computed repayment amount shown as deduction

### 4.2 Calculation Engine (runs client-side in JS)

For the selected area + household config, computes:

```
gross_income = (wage_1 × days_1 × 8 × 52) + (wage_2 × days_2 × 8 × 52)

student_loan_repayment = sum over persons of:
  if plan == N/A: 0
  elif plan == 1: max(0, (gross_1 - 25000) × 0.09)
  elif plan == 2: max(0, (gross_1 - 27295) × 0.09)
  elif plan == 4: max(0, (gross_1 - 31395) × 0.09)

income_tax = computed via UK bands (personal allowance 12570)
NI = 0 on first ~12.5k, 8% on 12.5k-50k, 2% above (employee rate)

benefits = UC + PIP_total + DLA_children_total + carers_allowance_if_eligible

costs = rent_monthly × 12 + council_tax_annual + utilities_annual + transport_annual

disposable = gross_income + benefits - tax - NI - student_loan - costs
```

**Benefits logic:**
- UC: means-tested, work allowance rules for LCWRA (16h threshold)
- PIP: rates per component (lower/middle/high care × lower/higher mobility)
- DLA child: rates per component × child count
- Carer's Allowance: if one person has high enough disability and other works <16h caring
- Benefit cap: £25,000/year for couples outside London; lifted if LCWRA or disabled child

### 4.3 Results Display

Each result row:
- Label
- Amount (£/year and £/month)
- Expandable note explaining how it was calculated

**Sensitivity panel:**
Quick "what if?" buttons:
- "1 more day work" — recalculates with +1 day for each working person
- "No kids" — recalculates with children removed
- "No disability claims" — shows what it would be without PIP/DLA
- "Cheapest area" — shows the best-value area for this config

### 4.4 Error & Edge States

- Missing required fields: inline validation, no submission
- Wage entered but 0 days: warn that wage has no effect
- Area not found: fallback to "UK average" values
- Disposable income negative: show in red with explanation
- Very high income (no benefits applicable): skip benefits section, note "outside benefits eligibility"

---

## 5. Component Inventory

### Input Components

**PersonCard**
- Collapsible card for each household adult
- States: disabled (Person 2 off), enabled, error (invalid wage)
- Contains: wage input, day selector (toggle buttons), disability dropdowns, student loan select, commute method

**ChildCounter**
- Three counters side by side
- +/− buttons with min=0, max=7
- Labels: "Non-disabled", "Lower disability", "Higher disability"

**AreaSelector**
- Searchable `<select>` or custom combobox
- Shows area name + region
- Loads pre-computed rent data for that area

**CommuteMethodSelector**
- Three toggle buttons: N/A, Car, Train
- Conditional sub-field: days worked + Motability eligibility (if high-rate PIP mobility)

**StudentLoanSelect**
- Four-option select: N/A, Plan 1, Plan 2, Plan 4

### Output Components

**ResultRow**
- Label + amount (annual + monthly)
- Expandable explanation (collapsed by default)
- Variants: income (green tint), deduction (red tint), benefit (blue tint)

**SensitivityButton**
- Compact button
- Shows "what if X?" label
- Triggers inline recalc, replaces result panel

**DisposableIncomeHero**
- Large display of final disposable income figure
- Colour coded: ≥£15k green, £8-15k amber, <£8k red

---

## 6. Technical Approach

### Architecture

```
benefits-uk/
├── SPEC.md
├── README.md
├── compute/
│   ├── compute.py          # Main precomputation script
│   ├── benefits.py         # Benefits calculation logic
│   ├── tax.py              # Income tax / NI logic
│   ├── areas.py            # ONS data +租金 lookup
│   └── requirements.txt
├── data/
│   ├── areas.json          # 7018 BUAs with rent/council tax data
│   └── output/
│       └── lookup.json     # Precomputed results (gitignored, generated)
├── www/
│   ├── index.html          # Single page app
│   ├── app.js              # Main calculation + UI logic
│   ├── data.js             # Embedded lookup data (or fetched)
│   └── style.css
├── .github/
│   └── workflows/
│       ├── compute.yml      # Runs precomputation on ONS data update
│       └── deploy.yml       # Deploys www/ to GitHub Pages
└── Makefile
```

### Precomputation (compute/)

Uses Python 3 + NumPy + pandas. Runs offline; pulls ONS data via CSV downloads.

**Inputs:**
- ONS Private Rental Market Statistics (CSV, quarterly, free)
- ONS Council Tax estimates per LA (CSV, free)
- Built-Up Areas list with coordinates (ONS, free)
- Hardcoded benefit rates (annual, from gov.uk)

**Outputs:**
- `data/areas.json` — per-BUa: rent estimates, council tax band average, lat/lon
- `data/lookup.json` — per-area, per-scenario: optimal child count + resulting disposable income

### Precomputation scope (v1)

Precompute for these scenario families only:
1. `single_no_disability`: Person 1, 0/2/5 days, no disability, no commute
2. `couple_no_disability`: Person 1 + Person 2, 0/2/5 each, no disability
3. `couple_commuting`: as above + car/train commute costs
4. `single_disability`: Person 1, 0/2/5 days, disability (all PIP combinations)
5. `couple_disability`: both persons with disability combinations
6. `with_children`: for each of the above, vary child count 0-7 in each DLA tier

For each: store minimum children needed to achieve each £1K income bracket £0-£25K.

### Data embedding

For v1: `data/lookup.json` is fetched on page load (gzip-compressed, ~5-10MB). If fetch fails, fall back to a sample dataset covering "average UK area" with a note.

### Deployment

GitHub Pages serves `www/` directory. No server required. `compute/` workflow runs on ONS data publication schedule (quarterly).

### Browser support

Modern browsers only (ES2020). No IE11. Progressive enhancement: works without JS for basic rent lookup, full functionality with JS.
