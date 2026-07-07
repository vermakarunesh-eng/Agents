# Geopolitical Analyst Agent

Python agent for trading apps that converts geopolitical signals into high-resolution confidence scores for:

- conflict escalation and de-escalation
- sanctions probability and market severity
- trade restriction and supply-chain disruption risk

The package is deliberately data-source agnostic. Feed it normalized observations from news, policy trackers, analyst notes, market data, or internal alerts. It returns calibrated scores, confidence intervals, impact estimates, and an audit trail of the reasoning factors.

## Quick Start

```powershell
python -m geopolitical_analyst.cli examples/sample_signal.json
```

## Integration Pattern

```python
from geopolitical_analyst import GeopoliticalAnalyst, Observation, Signal

agent = GeopoliticalAnalyst()
assessment = agent.assess([
    Observation(
        region="Red Sea",
        countries=["YEM", "USA", "GBR"],
        signal=Signal.CONFLICT,
        source_reliability=0.82,
        intensity=0.76,
        market_relevance=0.91,
        recency_hours=3,
        evidence="Missile interception report near commercial shipping lane.",
    )
])

print(assessment.overall_score)
print(assessment.recommendation)
```

## Score Meaning

Scores are continuous values from `0.0000` to `1.0000`.

- `0.00-0.20`: low probability or negligible trading impact
- `0.20-0.45`: monitor
- `0.45-0.65`: material risk
- `0.65-0.85`: high conviction risk
- `0.85-1.00`: extreme risk or active shock

Confidence is separate from risk. A high risk score with lower confidence means the scenario is serious but evidence quality or corroboration is thin.

