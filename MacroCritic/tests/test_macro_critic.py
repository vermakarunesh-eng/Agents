import unittest

from macro_critic import MacroCriticAgent, MacroSnapshot, MarketSnapshot, TradeProposal


class MacroCriticAgentTests(unittest.TestCase):
    def test_macro_critic_opposes_buy_in_hostile_macro_backdrop(self):
        proposal = TradeProposal(
            action="BUY",
            symbol="NEXA",
            asset_class="equity",
            sector="clean_energy",
            country="IN",
            horizon_days=30,
        )
        macro = MacroSnapshot(
            inflation_yoy=7.2,
            policy_bias="hawkish",
            gdp_growth_yoy=2.4,
            pmi=48.0,
            currency_change_30d_pct=-3.0,
            liquidity_condition="tightening",
            yield_curve_slope_bps=-20,
        )
        market = MarketSnapshot(
            index_trend_30d_pct=-4.0,
            sector_trend_30d_pct=-6.0,
            volatility_percentile=82,
            credit_spread_change_30d_bps=32,
        )

        result = MacroCriticAgent().critique(proposal, macro, market)

        self.assertEqual(result.stance, "oppose")
        self.assertLess(result.directional_confidence, 42)
        self.assertEqual(result.consensus_payload["recommended_direction"], "HOLD_OR_SELL")

    def test_macro_critic_supports_sell_in_hostile_macro_backdrop(self):
        proposal = TradeProposal(
            action="SELL",
            symbol="NEXA",
            asset_class="equity",
            sector="clean_energy",
            country="IN",
            horizon_days=30,
        )
        macro = MacroSnapshot(
            inflation_yoy=7.2,
            policy_bias="hawkish",
            gdp_growth_yoy=2.4,
            pmi=48.0,
            currency_change_30d_pct=-3.0,
            liquidity_condition="tightening",
        )
        market = MarketSnapshot(index_trend_30d_pct=-4.0, volatility_percentile=82)

        result = MacroCriticAgent().critique(proposal, macro, market)

        self.assertEqual(result.stance, "support")
        self.assertGreaterEqual(result.directional_confidence, 62)
        self.assertEqual(result.consensus_payload["recommended_direction"], "SELL")


if __name__ == "__main__":
    unittest.main()
