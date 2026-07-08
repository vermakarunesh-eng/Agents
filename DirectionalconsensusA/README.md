# Directional Consensus Agent A

Agent A is a deterministic investment-committee participant inspired by the directional confidence consensus workflow in the reference architecture. It converts market, fundamental, macro, sentiment, technical, and risk evidence into a directional recommendation with explainable confidence.

The agent is intentionally lightweight: no network calls, no external services, and no model dependency. That makes it easy to use as a reliable baseline agent inside a larger multi-agent committee.

## What It Does

- Scores each stock across fundamentals, technicals, sentiment, macro exposure, and risk.
- Produces a directional decision: `BUY`, `HOLD`, or `SELL`.
- Emits an explainable directional confidence score from `0` to `100`.
- Simulates committee-style consensus by combining Agent A with optional peer agent opinions.
- Returns forensic logs explaining which evidence changed the decision.

## Run

```powershell
python run_agent.py --input data/sample_market_snapshot.json
```

For JSON output:

```powershell
python run_agent.py --input data/sample_market_snapshot.json --json
```

If the package is installed, the equivalent console command is:

```powershell
directional-consensus-a --input data/sample_market_snapshot.json
```

## Input Shape

The input file contains:

- `portfolio`: current holdings.
- `candidates`: stocks to evaluate.
- `market_context`: shared market/macro state.
- `peer_opinions`: optional recommendations from other committee agents.

See [data/sample_market_snapshot.json](data/sample_market_snapshot.json) for a complete example.

## Design Notes

Agent A is biased toward high-signal, evidence-backed decisions:

- Strong balance sheet, revenue growth, and earnings quality increase confidence.
- Positive trend, momentum, and volume confirmation improve direction.
- Macro stress, volatility, drawdown, and negative news reduce confidence.
- Peer opinions are trusted only according to historical reliability and directional alignment.

This keeps Agent A useful as the “steady analyst” in a larger autonomous investment committee: it can disagree, but it must show its work.
