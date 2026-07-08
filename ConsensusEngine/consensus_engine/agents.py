from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from consensus_engine.models import Action, AgentVote, Evidence, MarketContext


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def best_symbol(
    context: MarketContext,
    metric_weights: dict[str, float],
    lower_is_better: Iterable[str] = (),
) -> tuple[str, float]:
    lower_metrics = set(lower_is_better)
    scored: list[tuple[str, float]] = []
    for symbol, data in context.candidates.items():
        score = 0.0
        for metric, weight in metric_weights.items():
            value = float(data.get(metric, 0.0))
            if metric in lower_metrics:
                value = -value
            score += value * weight
        scored.append((symbol, score))
    return max(scored, key=lambda item: item[1])


class FinancialAgent(ABC):
    agent_id: str

    @abstractmethod
    def evaluate(self, context: MarketContext) -> AgentVote:
        raise NotImplementedError

    def _vote(
        self,
        context: MarketContext,
        symbol: str,
        score: float,
        thesis: str,
        evidence: tuple[Evidence, ...],
        alternatives: tuple[str, ...] = (),
    ) -> AgentVote:
        action = Action.BUY if score > 0.04 else Action.HOLD
        confidence = clamp(0.52 + abs(score) * 1.35)
        return AgentVote(
            agent_id=self.agent_id,
            action=action,
            symbol=symbol,
            confidence=confidence,
            thesis=thesis,
            evidence=evidence,
            alternatives=alternatives,
        )


class MacroEconomistAgent(FinancialAgent):
    agent_id = "macro"

    def evaluate(self, context: MarketContext) -> AgentVote:
        policy = float(context.macro.get("clean_energy_policy_strength", 0.0))
        rates = float(context.macro.get("interest_rate_bias", 0.0))
        symbol, base = best_symbol(context, {"policy_tailwind": 0.7, "expected_return": 0.3})
        score = base + policy * 0.35 + rates * 0.15
        return self._vote(
            context,
            symbol,
            score,
            "Macro backdrop favors assets with policy tailwinds and positive growth regimes.",
            (
                Evidence("macro", f"Clean energy policy strength {policy:.2f}", abs(policy)),
                Evidence("macro", f"Interest-rate bias {rates:.2f}", abs(rates)),
            ),
        )


class FundamentalAnalystAgent(FinancialAgent):
    agent_id = "fundamental"

    def evaluate(self, context: MarketContext) -> AgentVote:
        symbol, score = best_symbol(
            context,
            {
                "revenue_growth": 0.45,
                "earnings_growth": 0.4,
                "debt_to_equity": 0.15,
            },
            lower_is_better=("debt_to_equity",),
        )
        data = context.candidates[symbol]
        return self._vote(
            context,
            symbol,
            score,
            "Fundamentals prefer stronger growth with cleaner leverage.",
            (
                Evidence("fundamentals", f"Revenue growth {data.get('revenue_growth', 0):.1%}", abs(float(data.get("revenue_growth", 0)))),
                Evidence("fundamentals", f"Earnings growth {data.get('earnings_growth', 0):.1%}", abs(float(data.get("earnings_growth", 0)))),
                Evidence("fundamentals", f"Debt/equity {data.get('debt_to_equity', 0):.2f}", 1.0 - clamp(float(data.get("debt_to_equity", 0)) / 3.0)),
            ),
        )


class TechnicalAnalystAgent(FinancialAgent):
    agent_id = "technical"

    def evaluate(self, context: MarketContext) -> AgentVote:
        symbol, score = best_symbol(
            context,
            {
                "price_momentum_20d": 0.35,
                "price_momentum_60d": 0.35,
                "macd": 0.2,
                "volume_surge": 0.1,
            },
        )
        data = context.candidates[symbol]
        rsi = float(data.get("rsi", 50))
        if rsi > 70:
            score -= 0.08
        return self._vote(
            context,
            symbol,
            score,
            "Technical structure favors momentum confirmed by volume without exhaustion.",
            (
                Evidence("technical", f"20-day momentum {data.get('price_momentum_20d', 0):.1%}", abs(float(data.get("price_momentum_20d", 0)))),
                Evidence("technical", f"MACD {data.get('macd', 0):.2f}", abs(float(data.get("macd", 0)))),
                Evidence("technical", f"RSI {rsi:.0f}", 1.0 - abs(rsi - 55) / 55),
            ),
        )


class SentimentAnalystAgent(FinancialAgent):
    agent_id = "sentiment"

    def evaluate(self, context: MarketContext) -> AgentVote:
        symbol, score = best_symbol(
            context,
            {"news_sentiment": 0.65, "social_sentiment": 0.35},
        )
        data = context.candidates[symbol]
        return self._vote(
            context,
            symbol,
            score,
            "Sentiment read-through prefers names with durable news and social support.",
            (
                Evidence("sentiment", f"News sentiment {data.get('news_sentiment', 0):.2f}", abs(float(data.get("news_sentiment", 0)))),
                Evidence("sentiment", f"Social sentiment {data.get('social_sentiment', 0):.2f}", abs(float(data.get("social_sentiment", 0)))),
            ),
        )


class GeopoliticalAnalystAgent(FinancialAgent):
    agent_id = "geopolitical"

    def evaluate(self, context: MarketContext) -> AgentVote:
        symbol, score = best_symbol(
            context,
            {"geopolitical_risk": 0.75, "expected_return": 0.25},
            lower_is_better=("geopolitical_risk",),
        )
        data = context.candidates[symbol]
        return self._vote(
            context,
            symbol,
            score,
            "Geopolitical screen favors lower exposure to conflict, sanctions, and trade shocks.",
            (
                Evidence("geopolitical", f"Geopolitical risk {data.get('geopolitical_risk', 0):.2f}", 1.0 - clamp(float(data.get("geopolitical_risk", 0)))),
            ),
        )


class GovernmentPolicyAgent(FinancialAgent):
    agent_id = "government_policy"

    def evaluate(self, context: MarketContext) -> AgentVote:
        symbol, score = best_symbol(context, {"policy_tailwind": 0.8, "expected_return": 0.2})
        data = context.candidates[symbol]
        return self._vote(
            context,
            symbol,
            score,
            "Policy analyst favors sectors with regulatory and fiscal tailwinds.",
            (
                Evidence("policy", f"Policy tailwind {data.get('policy_tailwind', 0):.2f}", abs(float(data.get("policy_tailwind", 0)))),
            ),
        )


class RiskAssessmentAgent(FinancialAgent):
    agent_id = "risk"

    def evaluate(self, context: MarketContext) -> AgentVote:
        symbol, score = best_symbol(
            context,
            {"volatility": 0.35, "max_drawdown": 0.45, "expected_return": 0.2},
            lower_is_better=("volatility", "max_drawdown"),
        )
        data = context.candidates[symbol]
        return self._vote(
            context,
            symbol,
            score,
            "Risk assessment prefers return per unit of volatility and drawdown.",
            (
                Evidence("risk", f"Volatility {data.get('volatility', 0):.1%}", 1.0 - clamp(float(data.get("volatility", 0)))),
                Evidence("risk", f"Max drawdown {data.get('max_drawdown', 0):.1%}", 1.0 - clamp(float(data.get("max_drawdown", 0)))),
            ),
        )


DEFAULT_AGENTS: tuple[FinancialAgent, ...] = (
    MacroEconomistAgent(),
    FundamentalAnalystAgent(),
    TechnicalAnalystAgent(),
    SentimentAnalystAgent(),
    GeopoliticalAnalystAgent(),
    GovernmentPolicyAgent(),
    RiskAssessmentAgent(),
)
