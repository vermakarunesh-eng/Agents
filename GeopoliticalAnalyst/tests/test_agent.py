import unittest

from geopolitical_analyst import GeopoliticalAnalyst, Observation, Recommendation, Signal, TimeHorizon


class GeopoliticalAnalystTests(unittest.TestCase):
    def test_conflict_signal_produces_high_resolution_scores(self) -> None:
        assessment = GeopoliticalAnalyst().assess(
            [
                Observation(
                    region="Red Sea",
                    countries=["YEM", "USA"],
                    signal=Signal.CONFLICT,
                    source_reliability=0.86,
                    intensity=0.88,
                    market_relevance=0.92,
                    recency_hours=2,
                    evidence="Commercial shipping rerouted after confirmed strike.",
                    asset_classes=["crude_oil", "shipping"],
                    corroboration_count=5,
                    novelty=0.65,
                    escalation_velocity=0.82,
                )
            ]
        )

        conflict = assessment.domain_scores[Signal.CONFLICT]

        self.assertGreater(conflict.score, 0.75)
        self.assertGreater(conflict.confidence, 0.65)
        self.assertEqual(conflict.horizon, TimeHorizon.INTRADAY)
        self.assertEqual(round(conflict.score, 4), conflict.score)
        self.assertIn(assessment.recommendation, {Recommendation.HEDGE, Recommendation.REDUCE_EXPOSURE})

    def test_empty_observations_return_no_actionable_risk(self) -> None:
        assessment = GeopoliticalAnalyst().assess([])

        self.assertEqual(assessment.overall_score, 0.0)
        self.assertEqual(assessment.overall_confidence, 0.0)
        self.assertEqual(assessment.recommendation, Recommendation.IGNORE)
        self.assertEqual(assessment.summary, "No actionable geopolitical signals were supplied.")

    def test_sanctions_are_driven_by_policy_specificity(self) -> None:
        low_specificity = Observation(
            region="Europe",
            countries=["RUS", "EU"],
            signal=Signal.SANCTIONS,
            source_reliability=0.75,
            intensity=0.55,
            market_relevance=0.8,
            recency_hours=24,
            evidence="General diplomatic warning.",
            policy_specificity=0.2,
            corroboration_count=2,
        )
        high_specificity = Observation(
            region="Europe",
            countries=["RUS", "EU"],
            signal=Signal.SANCTIONS,
            source_reliability=0.75,
            intensity=0.55,
            market_relevance=0.8,
            recency_hours=24,
            evidence="Draft package names banks, commodities, and enforcement date.",
            policy_specificity=0.9,
            corroboration_count=2,
        )

        agent = GeopoliticalAnalyst()
        low = agent.assess([low_specificity]).domain_scores[Signal.SANCTIONS]
        high = agent.assess([high_specificity]).domain_scores[Signal.SANCTIONS]

        self.assertGreater(high.score, low.score)
        self.assertEqual(high.drivers[0].name, "policy_specificity")


if __name__ == "__main__":
    unittest.main()
