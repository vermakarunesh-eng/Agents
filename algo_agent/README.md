# Algo Trade Recommendation Agent

A dependency-free Python research agent that trains a lightweight ML model on OHLCV price history, backtests the signal, and emits risk-aware trade recommendations.

This is not financial advice. It is a local research tool for screening and experimentation. Validate data, execution, fees, slippage, position sizing, and regulations before using any signal with real capital.

## What It Does

- Loads OHLCV data from a local CSV, generated synthetic sample, or Stooq daily CSV download.
- Builds technical features from only past data.
- Trains a logistic regression model with time-series validation.
- Converts model probability into `BUY`, `SELL`, or `HOLD`.
- Adds confidence, stop loss, take profit, position size, and rationale.
- Applies real-money review gates for model edge, liquidity, volatility, and spread proxy.
- Runs a simple backtest with transaction costs.
- Produces JSON for easy integration into a UI, bot, or broker adapter.

## Quick Start

```powershell
python -m algo_agent.cli recommend --symbol AAPL --demo
python -m algo_agent.cli backtest --symbol AAPL --demo
python -m algo_agent.cli reinforce --symbol AAPL --demo
```

Use your own CSV:

```powershell
python -m algo_agent.cli recommend --csv path\to\prices.csv --symbol RELIANCE
python -m algo_agent.cli backtest --csv path\to\prices.csv --symbol RELIANCE
```

Capital-aware recommendation:

```powershell
python -m algo_agent.cli recommend --csv path\to\prices.csv --symbol AAPL --capital 50000 --risk-pct 0.5 --max-position-pct 8
```

Expected CSV columns:

```text
date,open,high,low,close,volume
```

Column names are case-insensitive. Extra columns are ignored.

Try Stooq daily data, if network access is available:

```powershell
python -m algo_agent.cli recommend --symbol aapl.us --source stooq
```

## Example Output

```json
{
  "symbol": "AAPL",
  "action": "BUY",
  "confidence": 0.61,
  "model_probability_up": 0.64,
  "entry": 191.22,
  "stop_loss": 184.51,
  "take_profit": 203.31,
  "position_size_pct": 7.5,
  "shares": 19,
  "notional": 3633.18,
  "capital_at_risk": 127.49,
  "risk_reward": 1.8,
  "review_status": "APPROVED_FOR_REVIEW",
  "rationale": [
    "Model probability is above buy threshold.",
    "Short trend is above long trend.",
    "Volatility-adjusted risk allows a moderate position."
  ]
}
```

## Project Layout

```text
algo_agent/
  agent.py       Recommendation orchestration
  backtest.py    Walk-forward-ish signal backtest
  cli.py         Command-line interface
  data.py        CSV, synthetic, and Stooq loaders
  features.py    Technical feature generation
  model.py       Dependency-free logistic model
  risk.py        Sizing and trade levels
tests/
  test_agent.py
```

## Design Notes

The model predicts whether the close price will be higher after a configurable forward horizon. Signals are intentionally conservative:

- `BUY` requires enough model confidence plus positive trend confirmation.
- `SELL` is used when probability is low and trend is weak.
- `HOLD` is the default when evidence is mixed.

The backtest is simple by design. It is meant to catch obvious problems and compare strategy versions, not prove profitability.

## Reinforcement Learning

The `reinforce` command adds a small dependency-free Q-learning loop on top of the existing supervised signal. In simple terms, reinforcement learning means an agent tries actions, receives rewards, and gradually updates a policy toward actions that produced better outcomes.

In this package:

- **State** = model probability bucket, trend bucket, and volatility bucket.
- **Action** = `BUY`, `SELL`, or `HOLD`.
- **Reward** = next-bar trading return minus transaction cost and drawdown penalty.
- **Policy** = a Q-table showing the best learned action for each market state.

Run it with demo prices:

```powershell
python -m algo_agent.cli reinforce --demo --episodes 30
```

Run it with your own OHLCV CSV:

```powershell
python -m algo_agent.cli reinforce --csv path\to\prices.csv --symbol RELIANCE --episodes 40 --train-window 180
```

## Real-Money Guardrails

The agent will not mark a signal as `APPROVED_FOR_REVIEW` unless configured gates pass:

- validation accuracy beats the majority-class baseline by `--min-accuracy-edge`
- validation sample count is large enough
- average dollar volume is above `--min-dollar-volume`
- annualized volatility is below the policy maximum
- high/low spread proxy is not excessively wide

Even when approved, output is a research recommendation for human review, not an execution instruction.
