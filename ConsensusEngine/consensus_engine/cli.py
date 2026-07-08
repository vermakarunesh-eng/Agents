from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from consensus_engine.engine import ConsensusEngine
from consensus_engine.models import MarketContext


def load_payload(path: Path | None) -> dict[str, Any]:
    if path is None:
        path = Path(__file__).resolve().parents[1] / "examples" / "market_snapshot.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run directional confidence consensus over a market snapshot."
    )
    parser.add_argument("--input", type=Path, help="Path to a market snapshot JSON file.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()

    context = MarketContext.from_dict(load_payload(args.input))
    decision = ConsensusEngine().decide(context)
    indent = 2 if args.pretty else None
    print(json.dumps(decision.to_dict(), indent=indent))


if __name__ == "__main__":
    main()
