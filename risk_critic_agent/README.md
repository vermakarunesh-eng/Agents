# Risk Critic Agent

Integration-ready agent package for an investment committee workflow. The agent critiques proposed trades before execution and returns strict JSON for downstream orchestration.

## Files

- `risk_critic_prompt.md`: system prompt for the agent.
- `risk_critic_schema.json`: output contract for validation.
- `risk_critic_agent.py`: portable Python wrapper with prompt construction, parsing, validation, and a safe insufficient-data fallback.
- `sample_request.json`: example app payload.
- `sample_response.json`: example model output.

## Expected App Flow

1. Collect a proposed action, instrument, horizon, position size, market data, portfolio context, agent recommendations, and supporting evidence.
2. Normalize those inputs into the payload shape shown in `sample_request.json`.
3. Call your chat model using `RiskCriticAgent.build_messages(payload)`.
4. Parse and validate the returned JSON with `validate_output`.
5. Block, route, or allow the proposal based on `decision`, `human_review_required`, and `required_controls`.

## Python Integration

```python
import json
from risk_critic_agent import RiskCriticAgent


def call_model(messages, model_options):
    # Replace with your app's model client.
    # Return the model response as a raw JSON string.
    raise NotImplementedError


payload = json.load(open("sample_request.json", "r", encoding="utf-8"))
agent = RiskCriticAgent(model_caller=call_model, model_options={"temperature": 0.1})
critique = agent.run(payload)

if critique["decision"] in {"reject", "insufficient_data"}:
    block_trade(critique)
elif critique["human_review_required"]:
    escalate_to_human(critique)
else:
    attach_controls_to_order_ticket(critique["required_controls"])
```

## Suggested Decision Handling

- `approve_with_controls`: allow only after required controls are attached.
- `reduce_size`: send back to the portfolio manager with a lower max weight.
- `delay_for_confirmation`: pause order creation until listed evidence arrives.
- `hedge_required`: require hedge ticket linkage before execution.
- `reject`: block execution.
- `insufficient_data`: block execution and request missing fields.

## Minimum Payload Fields

The wrapper treats these fields as required for a responsible critique:

- `proposed_action`
- `instrument`
- `time_horizon`
- `portfolio_context`
- `market_data`
- `supporting_evidence`

The agent can accept more context than this, including agent reliability scores, prior committee logs, options data, event calendars, liquidity analytics, and risk-budget constraints.

## Notes

This agent is research support for an investment app. It should not fabricate data or provide personalized financial advice. If current market data or portfolio context is missing, the correct behavior is to return `insufficient_data` or demand confirmation before execution.
