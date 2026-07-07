# Fundamental Analyst Agent Runbook

This folder contains a runnable, dependency-free Fundamental Analyst agent.

## Files

- `fundamental_analyst_agent.py` - Python CLI scoring engine
- `company-financials-template.json` - blank input template for a real company
- `sample-company-financials.json` - filled sample input
- `sample-analysis-result.json` - structured sample output
- `sample-analysis-report.md` - Markdown sample report
- `sample-analysis-report.html` - browser-friendly sample report
- `fundamental-analyst-agent.md` - full agent behavior spec
- `fundamental-analyst-agent.schema.json` - machine-readable agent schema

## Run The Sample

From this folder's parent directory:

```powershell
python outputs\fundamental_analyst_agent.py outputs\sample-company-financials.json --json-out outputs\sample-analysis-result.json --md-out outputs\sample-analysis-report.md --html-out outputs\sample-analysis-report.html
```

## Analyze A Real Company

1. Copy `company-financials-template.json`.
2. Fill in the company's latest financial statement values.
3. Run:

```powershell
python outputs\fundamental_analyst_agent.py outputs\your-company.json --json-out outputs\your-company-result.json --md-out outputs\your-company-report.md --html-out outputs\your-company-report.html
```

## What The Agent Scores

The composite score uses these weights:

| Category | Weight |
|---|---:|
| Revenue Growth | 20% |
| Revenue Quality | 20% |
| Balance Sheet Strength | 25% |
| Profitability Support | 15% |
| Cash Conversion | 15% |
| Dilution And Capital Allocation | 5% |

The confidence score is separate from the quality score. It evaluates data freshness, statement coverage, audit reliability, consistency, and disclosure depth.

## Interpretation

- 90-100: exceptional
- 75-89: strong
- 60-74: acceptable
- 40-59: weak or mixed
- 20-39: poor
- 0-19: severe concern

Final views:

- Fundamentally Excellent
- Fundamentally Strong
- Fundamentally Mixed
- Fundamentally Weak
- Financially Distressed
- Insufficient Data

## Important Note

This is a financial statement analysis tool, not a buy/sell recommendation engine. It does not forecast stock price or replace professional investment advice.
