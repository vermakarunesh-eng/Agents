import unittest

from algo_agent.data import generate_demo_prices
from algo_agent.rl import ReinforcementLearningConfig, train_reinforcement_policy


class ReinforcementLearningTests(unittest.TestCase):
    def test_trains_q_learning_policy(self) -> None:
        bars = generate_demo_prices(days=180)
        result = train_reinforcement_policy(
            bars,
            config=ReinforcementLearningConfig(episodes=2, train_window=70),
        )

        self.assertEqual(result.episodes, 2)
        self.assertGreater(len(result.learned_rules), 0)
        self.assertIn(result.learned_rules[0].action, {"BUY", "SELL", "HOLD"})
        self.assertIsInstance(result.to_dict()["learned_rules"], list)


if __name__ == "__main__":
    unittest.main()
