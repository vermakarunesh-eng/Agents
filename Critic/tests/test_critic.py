from __future__ import annotations

import unittest

from critic_agent.critic import review_recommendation


def approved_payload() -> dict:
    return {
        "symbol": "TEST",
        "action": "BUY",
        "confidence": 0.64,
        "model_probability_up": 0.64,
        "entry": 100.0,
        "stop_loss": 96.0,
        "take_profit": 110.0,
        "position_size_pct": 5.0,
        "shares": 50,
        "notional": 5000.0,
        "capital_at_risk": 200.0,
        "risk_reward": 2.5,
        "review_status": "APPROVED_FOR_REVIEW",
        "policy_check": {"passed": True, "reasons": ["All configured real-money review gates passed."]},
        "model_metrics": {
            "accuracy": 0.62,
            "baseline_accuracy": 0.55,
            "precision": 0.64,
            "recall": 0.61,
            "samples": 100,
        },
        "top_features": [
            {"feature": "ret_10", "value": 0.03, "contribution": 0.2},
            {"feature": "rsi_14", "value": 0.58, "contribution": 0.1},
            {"feature": "volatility_20", "value": 0.2, "contribution": -0.05},
        ],
        "rationale": ["Model probability is above the buy threshold.", "Short trend is above long trend."],
    }


class CriticTests(unittest.TestCase):
    def test_passes_clean_recommendation(self) -> None:
        critique = review_recommendation(approved_payload())
        self.assertEqual(critique.verdict, "PASS")
        self.assertGreaterEqual(critique.score, 75)

    def test_rejects_policy_failure(self) -> None:
        payload = approved_payload()
        payload["review_status"] = "REJECTED_BY_POLICY"
        payload["policy_check"] = {"passed": False, "reasons": ["Model edge too low."]}
        critique = review_recommendation(payload)
        self.assertEqual(critique.verdict, "REJECT")

    def test_rejects_bad_trade_geometry(self) -> None:
        payload = approved_payload()
        payload["stop_loss"] = 105.0
        critique = review_recommendation(payload)
        self.assertEqual(critique.verdict, "REJECT")


if __name__ == "__main__":
    unittest.main()
