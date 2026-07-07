# Macroeconomist Agent

This deliverable defines a reusable macroeconomist agent for an investment app. It evaluates GDP growth, inflation, and interest rates, then returns regime labels, confidence scores, risks, and allocation tilts in a JSON-friendly structure.

## Files

- `macroeconomist_agent.py` - self-contained Python implementation with no third-party dependencies.
- `macroeconomist_agent_README.md` - integration notes.

## Agent Inputs

The app should pass validated `MacroObservation` records:

- `gdp_growth`: annualized quarterly GDP growth or a comparable real-growth measure.
- `inflation`: CPI, core CPI, PCE, or core PCE inflation.
- `policy_rate`: central-bank policy rate or effective policy-rate proxy.

Optional fields improve confidence scoring:

- `expected_value`: consensus or nowcast expectation.
- `prior_value`: previous period value.
- `recency_days`: age of the datapoint.
- `source_quality`: 0 to 1 score for the data source.
- `revision_risk`: 0 to 1 estimate of likely revision pressure.

## Confidence Method

Each indicator receives a high-resolution confidence score from 0 to 1. The score blends:

- source quality
- data recency
- revision stability
- surprise consistency versus expectations
- trend stability versus prior value

The overall confidence score blends:

- individual indicator confidence
- cross-signal macro alignment
- data completeness

## Run Demo

```powershell
python outputs\macroeconomist_agent.py
```

## Integration Pattern

```python
from outputs.macroeconomist_agent import MacroeconomistAgent, MacroObservation

agent = MacroeconomistAgent()
result = agent.analyze([
    MacroObservation(
        name="gdp_growth",
        value=2.4,
        unit="annualized_percent",
        period="latest_quarter",
        source="BEA/FRED",
        as_of="2026-07-07",
    ),
    MacroObservation(
        name="inflation",
        value=3.1,
        unit="year_over_year_percent",
        period="latest_month",
        source="BLS/FRED",
        as_of="2026-07-07",
    ),
    MacroObservation(
        name="policy_rate",
        value=4.5,
        unit="percent",
        period="current",
        source="Federal Reserve",
        as_of="2026-07-07",
    ),
])

payload = result.to_json()
```

## Production Notes

For live investment use, connect the input layer to trusted macro data providers such as BEA, BLS, FRED, central-bank feeds, Bloomberg, FactSet, or Refinitiv. The agent is designed to explain reasoning and confidence, not to replace compliance review, portfolio constraints, or human investment judgment.
