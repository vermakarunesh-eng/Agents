# Macro Critic Agent

Macro Critic is a specialist agent for an autonomous multi-agent investment committee. It challenges a proposed trade or allocation using macroeconomic evidence: inflation, growth, interest rates, liquidity, currency pressure, policy stance, market breadth, and regime risk.

The agent is designed to sit inside the debate and critic loop shown in the committee workflow. It does not make a final portfolio decision by itself. Instead, it produces a structured critique, a directional confidence score, evidence tags, and scenario risks that a consensus or execution agent can fuse with other analyst outputs.

## Quick Start

```powershell
python -m macro_critic.cli samples/macro_critic_input.json
```

The command prints JSON suitable for downstream agents.

## Input Contract

```json
{
  "proposal": {
    "action": "BUY",
    "symbol": "NEXA",
    "asset_class": "equity",
    "sector": "clean_energy",
    "country": "IN",
    "horizon_days": 30,
    "rationale": "Breakout with strong sentiment"
  },
  "macro": {
    "inflation_yoy": 5.1,
    "policy_rate": 6.5,
    "policy_bias": "hawkish",
    "gdp_growth_yoy": 6.8,
    "pmi": 58.3,
    "currency_change_30d_pct": -1.2,
    "liquidity_condition": "neutral",
    "yield_curve_slope_bps": 42,
    "fiscal_impulse": "supportive"
  },
  "market": {
    "index_trend_30d_pct": 4.2,
    "sector_trend_30d_pct": 8.4,
    "volatility_percentile": 61,
    "credit_spread_change_30d_bps": 8,
    "commodity_pressure": "rising"
  }
}
```

## Output Contract

The agent emits:

- `stance`: `support`, `caution`, or `oppose`
- `directional_confidence`: 0-100 score for the macro critique
- `summary`: committee-ready natural language assessment
- `evidence`: scored positive and negative macro signals
- `critic_comments`: direct challenges to the proposal
- `stress_scenarios`: risks that should be tested before execution
- `consensus_payload`: compact fields for a directional consensus agent

## Design Notes

- BUY decisions are penalized by restrictive policy, inflation pressure, weak growth, currency stress, liquidity tightening, and risk-off markets.
- SELL decisions are scored inversely: the same hostile macro backdrop can support reducing exposure.
- The agent intentionally separates evidence from verdict so a consensus layer can apply directional trust weighting and historical reliability.

