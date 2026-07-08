# Opportunity Critic Agent

This package implements the Opportunity Critic from the investment committee
workflow. It is the adversarial agent that asks: "Is there a better place to put
this capital than the current proposal?"

## What It Does

- Scores the current investment proposal against alternative candidates.
- Rewards expected return, conviction, liquidity, catalysts, and valuation.
- Penalizes downside risk.
- Adjusts confidence using evidence quality.
- Produces a committee-ready verdict:
  - `support_current`
  - `challenge_current`
  - `escalate_to_debate`

## Files

- `opportunity_critic.py` - typed Python implementation.
- `prompts.md` - LLM role prompt and output schema.
- `example.py` - runnable example with mock investment candidates.

## Run

```powershell
python .\example.py
```

## Integration Point

Call `OpportunityCriticAgent().critique(current_proposal, alternatives)` after
the financial analysis agents finish their research and before directional
consensus. Feed the returned `Critique` into the debate loop and consensus agent.

The agent should receive candidates from:

- Fundamental analyst
- Technical analyst
- Macro analyst
- Risk analyst
- Sentiment analyst
- Sector and peer screeners

## Tuning

Use `OpportunityCriticConfig` to change escalation thresholds and scoring
weights. For example, lower `min_improvement_to_challenge` if the committee
wants the critic to be more aggressive.
