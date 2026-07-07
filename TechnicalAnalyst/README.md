# TechnicalAnalyst Agent

Dependency-free Python agent for high-resolution technical confidence scoring using RSI, EMA trend structure, MACD momentum, and volume confirmation.

The agent emits separate scores for:

- `directional_score`: bullish or bearish technical evidence on a 0-100 scale.
- `confidence_score`: reliability of the signal based on indicator confidence, history depth, volume validity, and volatility.
- `conviction_score`: blended directional and confidence score for ranking opportunities.

This is research output only, not financial advice or an execution instruction.

## Quick Start

```powershell
python -m technical_analyst_agent.cli --demo --symbol DEMO
```

Use your own CSV:

```powershell
python -m technical_analyst_agent.cli --csv path\to\prices.csv --symbol AAPL
```

Expected CSV columns are case-insensitive:

```text
date,open,high,low,close,volume
```

## Scoring Model

The weighted directional score uses:

- RSI Momentum: 22%
- EMA Trend Structure: 30%
- MACD Momentum: 28%
- Volume Confirmation: 20%

Each component includes evidence and its own confidence score. The final action is conservative:

- `BUY` when directional score is at least 66 and confidence is at least 45.
- `SELL` when directional score is at most 34 and confidence is at least 45.
- `HOLD` otherwise.

## Python API

```python
from technical_analyst_agent import TechnicalAnalystAgent, load_csv

bars = load_csv("prices.csv")
result = TechnicalAnalystAgent().analyze(bars, symbol="AAPL")
print(result.to_dict())
```
