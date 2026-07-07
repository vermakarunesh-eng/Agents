# Trade Recommendation Critic Agent

A standalone reviewer for the Algo trade recommendation agent. It consumes recommendation JSON, checks the evidence and risk controls, and returns a structured critique with a final verdict.

The critic is intentionally skeptical. Its job is to protect capital by finding weak model evidence, missing fields, invalid risk/reward, oversized positions, policy rejections, and inconsistent recommendations.

## Quick Start

Review a recommendation file:

```powershell
python -m critic_agent.cli review --input recommendation.json
```

Pipe directly from the Algo agent:

```powershell
python C:\Heckathon2026\Algo\algo_agent\cli.py recommend --symbol DEMO --demo |
  python -m critic_agent.cli review
```

From inside this folder:

```powershell
cd C:\Heckathon2026\Critic
python -m unittest discover -s tests
```

## Verdicts

- `PASS`: Review gates are clean enough for human consideration.
- `CAUTION`: The idea may be worth research, but one or more issues need attention.
- `REJECT`: Do not trade without fixing the flagged issues.

The critic does not provide financial advice and does not execute trades.
