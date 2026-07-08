import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from directional_consensus_a import DirectionalConsensusAgentA, MarketSnapshot


def _snapshot_payload():
    return {
        "portfolio": [],
        "market_context": {
            "index_trend": "bullish",
            "inflation_trend": "falling",
            "interest_rate_outlook": "neutral",
            "risk_regime": "balanced",
        },
        "candidates": [
            {
                "symbol": "NEXA",
                "name": "Nexa Renewables",
                "sector": "Clean Energy",
                "current_price": 642.5,
                "revenue_growth_pct": 24.0,
                "profit_margin_pct": 18.5,
                "debt_to_equity": 0.62,
                "rsi": 58.0,
                "ema_signal": "bullish",
                "volume_ratio": 1.45,
                "news_sentiment": 0.52,
                "social_sentiment": 0.34,
                "macro_sensitivity": 0.82,
                "volatility_pct": 21.0,
                "max_drawdown_pct": 12.5,
                "beta": 1.08,
            },
            {
                "symbol": "WEAK",
                "name": "Weak Industries",
                "sector": "Cyclical",
                "current_price": 92.0,
                "revenue_growth_pct": -8.0,
                "profit_margin_pct": 2.0,
                "debt_to_equity": 2.4,
                "rsi": 78.0,
                "ema_signal": "bearish",
                "volume_ratio": 0.7,
                "news_sentiment": -0.4,
                "social_sentiment": -0.3,
                "macro_sensitivity": 0.9,
                "volatility_pct": 41.0,
                "max_drawdown_pct": 32.0,
                "beta": 1.7,
            },
        ],
        "peer_opinions": [
            {
                "agent_id": "Agent B",
                "symbol": "NEXA",
                "action": "BUY",
                "confidence": 75.0,
                "historical_reliability": 0.8,
            }
        ],
    }


class DirectionalConsensusAgentTests(unittest.TestCase):
    def test_agent_selects_best_directional_candidate(self):
        snapshot = MarketSnapshot.from_dict(_snapshot_payload())
        result = DirectionalConsensusAgentA().decide(snapshot)

        self.assertEqual(result.selected.symbol, "NEXA")
        self.assertEqual(result.selected.action, "BUY")
        self.assertGreater(result.consensus_confidence, result.selected.confidence)
        self.assertEqual(result.alternatives[0].symbol, "WEAK")

    def test_json_output_contains_forensic_log(self):
        snapshot = MarketSnapshot.from_dict(_snapshot_payload())
        result = DirectionalConsensusAgentA().decide(snapshot).to_dict()

        self.assertEqual(result["selected"]["symbol"], "NEXA")
        self.assertTrue(result["forensic_log"])
        self.assertIn("peer_alignment", result)


if __name__ == "__main__":
    unittest.main()
