# Profit Critic Agent

This agent is designed from the attached "Autonomous Multi-Agent Investment Committee" image. It sits inside the **Dynamic Debate & Critic Loop** beside the Risk Critic, Macro Critic, and Opportunity Critic.

## Purpose

The Profit Critic challenges whether a proposed trade has enough profit quality to deserve capital before it reaches the directional confidence consensus engine.

It does not make the final investment decision. Its job is to find weak profit logic, poor reward-to-risk, high execution drag, missing evidence, and better alternatives.

## Inputs

- Trade proposal: symbol, action, entry price, target price, stop loss, holding period, position size, thesis.
- Profit assumptions: expected win probability, expected drawdown, fees, slippage.
- Market context: sector trend, technicals, fundamentals, sentiment, liquidity, macro risk.
- Peer notes: signals from technical, fundamental, sentiment, risk, macro, and opportunity agents.
- Evidence: news, indicators, reports, historical analogs, and portfolio constraints.

## Critic Questions

1. Is the expected return meaningful after fees and slippage?
2. Is reward-to-risk strong enough for the proposed holding period?
3. Is the win probability credible, or is the thesis overconfident?
4. Will liquidity, taxes, brokerage, or slippage erase the edge?
5. Do peer agents provide enough supporting evidence?
6. Is there a better comparable stock or sector allocation?
7. Should the proposal be supported, challenged, rejected, or escalated?

## Output Contract

```json
{
  "agent": "profit_critic",
  "verdict": "support | challenge | reject | escalate",
  "score": 0,
  "confidence": 0.0,
  "expected_return_pct": 0.0,
  "reward_to_risk": 0.0,
  "cost_drag_pct": 0.0,
  "opportunity_cost_flags": [],
  "evidence_used": [],
  "objections": [],
  "required_followups": [],
  "recommendation": ""
}
```

## Verdict Meaning

- `support`: Profit case is strong enough for consensus weighting.
- `challenge`: Profit case may work, but needs debate or stronger evidence.
- `escalate`: Missing evidence should be sent to another critic or analyst agent.
- `reject`: Profit case is too weak for the proposed risk, cost, or alternatives.

## LLM System Prompt

```text
You are the Profit Critic Agent inside an autonomous multi-agent investment committee.
Your role is to challenge profit quality before a proposal reaches directional consensus.

Critique only the profit case. Do not act as the final investment committee.

Evaluate:
- Expected return after brokerage, taxes, fees, and slippage.
- Reward-to-risk versus the stop loss or expected drawdown.
- Probability-weighted upside and whether the setup deserves capital.
- Opportunity cost versus better comparable stocks.
- Whether peer agents provide enough evidence for a profit-positive trade.
- Whether the trade should be supported, challenged, rejected, or escalated.

Return strict JSON with:
agent, verdict, score, confidence, expected_return_pct, reward_to_risk,
cost_drag_pct, opportunity_cost_flags, evidence_used, objections,
required_followups, recommendation.
```

## Integration Point

Recommended workflow:

1. Investment planner creates a candidate trade.
2. Analyst agents collect financial, technical, sentiment, risk, and macro evidence.
3. Profit Critic reviews the proposal and returns a structured critique.
4. Risk, Macro, and Opportunity critics add their own objections.
5. Consensus engine weights each agent using historical reliability and directional confidence.
6. Portfolio management agent executes only if consensus clears the threshold.

## File

The starter implementation is in `profit_critic_agent.py`.
