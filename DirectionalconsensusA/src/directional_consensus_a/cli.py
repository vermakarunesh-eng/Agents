from __future__ import annotations

import argparse
import json
from pathlib import Path

from .agent import DirectionalConsensusAgentA
from .models import MarketSnapshot


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Directional Consensus Agent A on a market snapshot."
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to a market snapshot JSON file.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON instead of a committee summary.",
    )
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    snapshot = MarketSnapshot.from_dict(payload)
    result = DirectionalConsensusAgentA().decide(snapshot)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
        return 0

    selected = result.selected
    print("Directional Consensus Agent A")
    print("=" * 31)
    print(
        f"Decision: {selected.action} {selected.symbol} ({selected.stock_name}) "
        f"with {selected.confidence:.1f}% agent confidence"
    )
    print(f"Consensus confidence: {result.consensus_confidence:.1f}%")
    print(f"Expected return: {selected.expected_return_pct:+.1f}%")
    print(f"Expected drawdown: {selected.expected_drawdown_pct:.1f}%")
    print()
    print("Rationale")
    for item in selected.rationale:
        print(f"- {item}")
    print()
    print("Evidence")
    for item in selected.evidence:
        print(
            f"- {item.category}: {item.score:+.1f} "
            f"(weight {item.weight:.2f}) - {item.explanation}"
        )
    if result.alternatives:
        print()
        print("Alternatives")
        for item in result.alternatives:
            print(
                f"- {item.action} {item.symbol}: score {item.directional_score:+.1f}, "
                f"confidence {item.confidence:.1f}%"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
