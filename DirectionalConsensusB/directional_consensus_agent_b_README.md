# Directional Consensus Agent B

This deliverable implements **Agent B** for the directional confidence consensus
workflow shown in the reference image.

Agent B is intentionally modeled as a moderate-confidence analyst whose
committee influence rises when it disagrees with consensus and has a strong
historical record of correct disagreement.

## Run

```powershell
python .\directional_consensus_agent_b.py
```

Or pass a JSON payload:

```powershell
python .\directional_consensus_agent_b.py --input .\payload.json
```

## Input Shape

```json
{
  "symbol": "NEXA",
  "evidence": [
    {
      "name": "technical_breakout",
      "direction": "BUY",
      "strength": 0.69,
      "reliability": 0.71,
      "notes": "Price broke above resistance with expanding volume."
    }
  ],
  "context": {
    "current_consensus": "SELL",
    "consensus_confidence": 0.56,
    "market_regime_risk": 0.31,
    "peer_alignment": {
      "Agent A": "SELL",
      "Agent D": "HOLD"
    }
  }
}
```

## Output Shape

The agent returns:

- `action`: `BUY`, `HOLD`, or `SELL`
- `confidence`: Agent B's confidence in its own recommendation
- `influence_weight`: how strongly the committee should weight Agent B
- `directional_scores`: evidence distribution across directions
- `agrees_with_consensus`: whether Agent B agrees with current consensus
- `reasoning`: forensic trace for audit logs
- `evidence_used`: normalized evidence records with weighted signal values

