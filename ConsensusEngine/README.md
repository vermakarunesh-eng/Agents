# Autonomous Multi-Agent Investment Consensus Engine

This project implements the workflow in the reference diagram: a planner chooses specialized financial analysis agents, their recommendations enter a critic/debate loop, and a directional trust-aware consensus layer fuses evidence into a final investment committee decision with forensic logs.

The engine is deterministic and dependency-free by default, so it can be used in hackathon demos, tests, or wrapped by an API later.

## Run the demo

```powershell
python -m consensus_engine.cli --pretty
```

## Run with a JSON input

```powershell
python -m consensus_engine.cli --input examples/market_snapshot.json --pretty
```

## Run tests

```powershell
python -m unittest discover -s tests
```

## Core concepts

- **Planner**: selects relevant analysis agents from the available market context.
- **Specialized agents**: macro, fundamental, technical, sentiment, geopolitical, government policy, and risk assessment.
- **Critic loop**: risk, profit, macro, and opportunity critics challenge the current proposal.
- **Directional trust consensus**: weights each agent by confidence, evidence quality, reliability, and historical directional trust.
- **Forensic output**: emits final action, confidence score, reasoning, evidence used, alternatives, debate comments, risk/return, and a compact execution summary.
