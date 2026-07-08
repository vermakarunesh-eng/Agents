from __future__ import annotations

import json
import unittest
from pathlib import Path

from consensus_engine.engine import ConsensusEngine
from consensus_engine.models import Action, MarketContext


ROOT = Path(__file__).resolve().parents[1]


class ConsensusEngineTests(unittest.TestCase):
    def load_context(self) -> MarketContext:
        payload = json.loads((ROOT / "examples" / "market_snapshot.json").read_text())
        return MarketContext.from_dict(payload)

    def test_demo_snapshot_rotates_into_nexa(self) -> None:
        decision = ConsensusEngine().decide(self.load_context())

        self.assertEqual(decision.primary.action, Action.BUY)
        self.assertEqual(decision.primary.symbol, "NEXA")
        self.assertIsNotNone(decision.exit_instruction)
        self.assertEqual(decision.exit_instruction.symbol, "AETHER")
        self.assertGreater(decision.directional_confidence_score, 0.45)

    def test_forensic_log_contains_agent_scores(self) -> None:
        decision = ConsensusEngine().decide(self.load_context())

        self.assertIn("agents_consulted", decision.forensic_log)
        self.assertIn("raw_scores", decision.forensic_log)
        self.assertGreaterEqual(len(decision.weighted_votes), 6)

    def test_critics_are_recorded(self) -> None:
        decision = ConsensusEngine().decide(self.load_context())

        self.assertTrue(any(item.critic_id == "risk_critic" for item in decision.critiques))
        self.assertGreaterEqual(decision.expected_return, 0.2)


if __name__ == "__main__":
    unittest.main()
