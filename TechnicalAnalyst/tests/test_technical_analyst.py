import unittest

from technical_analyst_agent import TechnicalAnalystAgent, generate_demo_prices


class TechnicalAnalystAgentTests(unittest.TestCase):
    def test_agent_returns_high_resolution_scores(self) -> None:
        bars = generate_demo_prices(days=260)
        result = TechnicalAnalystAgent().analyze(bars, symbol="demo")

        self.assertEqual(result.symbol, "DEMO")
        self.assertIn(result.action, {"BUY", "SELL", "HOLD"})
        self.assertGreaterEqual(result.directional_score, 0)
        self.assertLessEqual(result.directional_score, 100)
        self.assertGreaterEqual(result.confidence_score, 0)
        self.assertLessEqual(result.confidence_score, 100)
        self.assertGreaterEqual(result.conviction_score, 0)
        self.assertLessEqual(result.conviction_score, 100)
        self.assertEqual(len(result.signals), 4)
        self.assertEqual(
            {signal.name for signal in result.signals},
            {
                "RSI Momentum",
                "EMA Trend Structure",
                "MACD Momentum",
                "Volume Confirmation",
            },
        )

    def test_result_serializes_to_plain_dict(self) -> None:
        result = TechnicalAnalystAgent().analyze(generate_demo_prices(), symbol="xyz")
        payload = result.to_dict()

        self.assertEqual(payload["symbol"], "XYZ")
        self.assertIsInstance(payload["latest"]["rsi_14"], float)
        self.assertIsInstance(payload["signals"][0]["evidence"], str)


if __name__ == "__main__":
    unittest.main()
