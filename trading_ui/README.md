# Agents Trading UI

Local browser dashboard for the repository's `algo_agent` recommendation engine and broker execution flow.

## Run

```powershell
python -m trading_ui.server --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765`.

## What it does

- Fetches live intraday quotes from Yahoo Finance, with Stooq daily history as a fallback.
- Uses `algo_agent.recommend` for action, confidence, stops, targets, sizing, rationale, and policy gates.
- Shows a recent price chart from live or daily bars.
- Executes broker orders through the Alpaca Trading API only when explicitly configured and enabled.
- Blocks execution unless the agent returns `BUY` or `SELL`, policy gates pass, confidence is high enough, and the cooldown has expired.
- Stores a local execution audit log in `trading_ui/execution_audit.json`.

## Live execution configuration

Set these environment variables before starting the server:

```powershell
$env:ALGO_LIVE_TRADING_ENABLED = "true"
$env:ALPACA_KEY_ID = "your-key-id"
$env:ALPACA_SECRET_KEY = "your-secret-key"
$env:ALPACA_BASE_URL = "https://api.alpaca.markets"
python -m trading_ui.server --host 127.0.0.1 --port 8765
```

The dashboard uses `POST /v2/orders` on the configured Alpaca base URL. Bracket orders include the agent stop loss and take profit.

## Safety boundary

Broker execution is disabled unless `ALGO_LIVE_TRADING_ENABLED=true` and broker credentials are present. The agent output remains research only, not financial advice. Review regulations, broker account permissions, slippage, fees, and risk controls before enabling live trading.
