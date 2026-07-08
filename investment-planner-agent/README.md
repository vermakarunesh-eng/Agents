# Investment Planner Agent

A runnable Python scaffold for the autonomous multi-agent investment committee shown in the reference diagram.

It implements:

- Investment Planner Agent for goal setting and specialist selection
- Diverse analyst agents: macro, fundamentals, technicals, sentiment, policy, geopolitical, risk, and opportunity critic
- Dynamic critic loop
- Directional trust-aware consensus and evidence fusion
- Portfolio allocation and forensic decision logs

This is a research/planning prototype. It does not fetch live prices or place trades. Feed it verified market data before using it in any real workflow.

## Run

```powershell
python investment_planner_agent.py --input sample_request.json
```

## Output

The CLI prints a final investment committee decision containing:

- ranked actions
- agent recommendations
- directional confidence score
- evidence used
- critic comments
- portfolio allocation proposal
- forensic logs

## Extend

Add live data connectors by replacing `load_request()` or by creating adapters that emit the same JSON shape as `sample_request.json`.

