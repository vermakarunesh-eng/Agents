# Atlas Committee Trading App

World-class demo UI for the autonomous multi-agent investment committee.

## What it uses

- Existing consensus code from `C:\Heckathon2026\Agents\ConsensusEngine`
- US paper-market candidate universe: NVDA, MSFT, AAPL, AMZN, TSLA, JPM
- $10,000 virtual capital with 1:2 leverage
- Directional confidence-aware consensus, agent weights, critic feedback, evidence, alternatives, costs, trade history, and forensic decision logs

## Run

```powershell
cd C:\Users\Owner\Documents\Codex\2026-07-08\bu-3\outputs\trading_app
C:\Python314\python.exe app.py
```

Open:

```text
http://127.0.0.1:8765
```

## API

- `GET /api/snapshot` returns the current portfolio, candidates, decision, trades, and logs.
- `GET /api/decision` returns the latest committee decision.
- `POST /api/step` advances the market, asks the committee for a decision, executes paper trading, and logs the result.
- `POST /api/reset` resets the trading session.
