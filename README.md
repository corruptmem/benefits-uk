# UK Benefits & Disposable Income Calculator

A static, privacy-first calculator that helps you understand how different life configurations affect your disposable income after taxes, housing, benefits, and transport costs across the UK.

**All calculation runs in your browser — no data is sent anywhere.**

## Features

- Calculates Universal Credit, PIP, DLA Child, Carer's Allowance, and Child Benefit
- Models the 16-hour work threshold and benefit cap rules
- Handles student loan repayments across Plan 1, Plan 2, and Plan 4
- Sensitivity analysis: "what if you worked 1 more day?", "no kids", etc.
- Static — works offline, no server required
- Deploys to GitHub Pages in seconds

## Development

```bash
# Install dependencies
pip install -r compute/requirements.txt

# Run precomputation (generates data/lookup.json)
python -m compute.compute

# Serve locally
python -m http.server 8080 --directory www
# Then open http://localhost:8080
```

## Precomputation

The `compute/` directory contains the Python precomputation scripts. These generate the lookup tables used by the web app.

```bash
# Generate lookup table (with UK average)
python -m compute.compute

# Compress output
python -m compute.compute --gzip

# Custom child range
python -m compute.compute --max-kids 5
```

## Deployment

GitHub Pages serves the `www/` directory directly. Push to `main` and GitHub Pages will update automatically.

## Benefit Data

Rates are from UK government sources for the 2024/25 tax year. This is an unofficial tool — always verify with official sources like [gov.uk benefits calculators](https://www.gov.uk/benefits-calculators).
