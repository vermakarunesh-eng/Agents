from __future__ import annotations

from collections import Counter

from consensus_engine.agents import DEFAULT_AGENTS, FinancialAgent
from consensus_engine.critics import DEFAULT_CRITICS, Critic
from consensus_engine.models import (
    Action,
    ConsensusDecision,
    Critique,
    Evidence,
    MarketContext,
    TradeInstruction,
)
from consensus_engine.trust import score_by_symbol, weight_votes


class InvestmentPlanner:
    def __init__(self, agents: tuple[FinancialAgent, ...] = DEFAULT_AGENTS) -> None:
        self._agents = agents

    def select_agents(self, context: MarketContext) -> tuple[FinancialAgent, ...]:
        selected: list[FinancialAgent] = []
        available_metrics = {
            metric
            for candidate in context.candidates.values()
            for metric in candidate.keys()
        }
        for agent in self._agents:
            if agent.agent_id == "macro" and context.macro:
                selected.append(agent)
            elif agent.agent_id == "fundamental" and "revenue_growth" in available_metrics:
                selected.append(agent)
            elif agent.agent_id == "technical" and "price_momentum_20d" in available_metrics:
                selected.append(agent)
            elif agent.agent_id == "sentiment" and "news_sentiment" in available_metrics:
                selected.append(agent)
            elif agent.agent_id == "geopolitical" and "geopolitical_risk" in available_metrics:
                selected.append(agent)
            elif agent.agent_id == "government_policy" and "policy_tailwind" in available_metrics:
                selected.append(agent)
            elif agent.agent_id == "risk" and "max_drawdown" in available_metrics:
                selected.append(agent)
        return tuple(selected)


class ConsensusEngine:
    def __init__(
        self,
        planner: InvestmentPlanner | None = None,
        critics: tuple[Critic, ...] = DEFAULT_CRITICS,
    ) -> None:
        self._planner = planner or InvestmentPlanner()
        self._critics = critics

    def decide(self, context: MarketContext) -> ConsensusDecision:
        agents = self._planner.select_agents(context)
        votes = [agent.evaluate(context) for agent in agents]
        weighted_votes = weight_votes(votes, context)
        scores = score_by_symbol(weighted_votes)
        winner = max(scores, key=scores.get)
        confidence = self._directional_confidence(winner, scores, weighted_votes)

        critiques = self._review(winner, context)
        confidence = self._apply_critique_penalty(confidence, critiques)

        current_symbol = self._current_position_symbol(context)
        exit_instruction = None
        if current_symbol and current_symbol != winner:
            exit_instruction = self._build_instruction(
                Action.SELL,
                current_symbol,
                0.75,
                "Capital is being rotated into the higher-confidence consensus candidate.",
                context,
            )

        primary = self._build_instruction(
            Action.BUY,
            winner,
            confidence,
            self._rationale(winner, votes, critiques, context),
            context,
        )

        alternatives = self._alternatives(winner, scores, critiques, context)
        evidence = self._evidence_for(winner, votes)
        reasoning = self._reasoning(winner, votes, weighted_votes, critiques, context)
        winner_data = context.candidates[winner]

        return ConsensusDecision(
            primary=primary,
            exit_instruction=exit_instruction,
            directional_confidence_score=confidence,
            consensus_reasoning=tuple(reasoning),
            evidence_used=tuple(evidence),
            alternatives_considered=tuple(alternatives),
            critiques=tuple(critiques),
            weighted_votes=tuple(weighted_votes),
            expected_return=float(winner_data.get("expected_return", 0.0)),
            expected_drawdown=float(winner_data.get("max_drawdown", 0.0)),
            forensic_log={
                "as_of": context.as_of,
                "agents_consulted": [agent.agent_id for agent in agents],
                "raw_scores": {key: round(value, 6) for key, value in scores.items()},
                "vote_distribution": dict(Counter(vote.symbol for vote in votes)),
            },
        )

    def _review(self, symbol: str, context: MarketContext) -> list[Critique]:
        return [
            critique
            for critic in self._critics
            if (critique := critic.review(symbol, context)) is not None
        ]

    def _apply_critique_penalty(
        self, confidence: float, critiques: list[Critique]
    ) -> float:
        penalty = sum(item.severity for item in critiques) * 0.035
        return max(0.0, min(1.0, confidence - penalty))

    def _directional_confidence(
        self, symbol: str, scores: dict[str, float], weighted_votes: list
    ) -> float:
        total_weight = sum(item.weight for item in weighted_votes) or 1.0
        score_strength = scores[symbol] / total_weight
        average_agent_confidence = (
            sum(item.vote.confidence for item in weighted_votes) / len(weighted_votes)
            if weighted_votes
            else 0.0
        )
        average_reliability = (
            sum(item.components["reliability"] for item in weighted_votes)
            / len(weighted_votes)
            if weighted_votes
            else 0.0
        )
        calibrated = score_strength * average_agent_confidence * average_reliability
        return max(0.0, min(1.0, 0.4 + calibrated * 0.75))

    def _build_instruction(
        self,
        action: Action,
        symbol: str,
        confidence: float,
        rationale: str,
        context: MarketContext,
    ) -> TradeInstruction:
        return TradeInstruction(
            action=action,
            symbol=symbol,
            name=str(context.candidates.get(symbol, {}).get("name", symbol)),
            confidence=confidence,
            rationale=rationale,
        )

    def _current_position_symbol(self, context: MarketContext) -> str | None:
        positions = context.portfolio.get("positions", {})
        if not positions:
            return None
        return max(
            positions,
            key=lambda symbol: float(positions[symbol].get("market_value", 0.0)),
        )

    def _rationale(
        self,
        symbol: str,
        votes: list,
        critiques: list[Critique],
        context: MarketContext,
    ) -> str:
        supporters = [vote.agent_id for vote in votes if vote.symbol == symbol]
        name = context.candidates[symbol].get("name", symbol)
        if critiques:
            return (
                f"{name} has the strongest directional consensus after critique, "
                f"supported by {', '.join(supporters)} with risks explicitly logged."
            )
        return f"{name} has the strongest directional consensus, supported by {', '.join(supporters)}."

    def _alternatives(
        self,
        winner: str,
        scores: dict[str, float],
        critiques: list[Critique],
        context: MarketContext,
    ) -> list[str]:
        alternatives = [
            symbol
            for symbol, _ in sorted(scores.items(), key=lambda item: item[1], reverse=True)
            if symbol != winner
        ][:3]
        candidate_fallbacks = sorted(
            (
                (
                    symbol,
                    float(data.get("expected_return", 0.0))
                    - float(data.get("max_drawdown", 0.0)) * 0.25,
                )
                for symbol, data in context.candidates.items()
                if symbol != winner
            ),
            key=lambda item: item[1],
            reverse=True,
        )
        for symbol, _ in candidate_fallbacks:
            if len(alternatives) >= 3:
                break
            if symbol not in alternatives:
                alternatives.append(symbol)
        for critique in critiques:
            if critique.suggested_symbol and critique.suggested_symbol not in alternatives:
                alternatives.append(critique.suggested_symbol)
        return alternatives

    def _evidence_for(self, symbol: str, votes: list) -> list[Evidence]:
        evidence: list[Evidence] = []
        for vote in votes:
            if vote.symbol == symbol:
                evidence.extend(vote.evidence)
        return sorted(evidence, key=lambda item: item.strength, reverse=True)[:8]

    def _reasoning(
        self,
        symbol: str,
        votes: list,
        weighted_votes: list,
        critiques: list[Critique],
        context: MarketContext,
    ) -> list[str]:
        name = context.candidates[symbol].get("name", symbol)
        supporters = [vote.agent_id for vote in votes if vote.symbol == symbol]
        top_weights = sorted(weighted_votes, key=lambda item: item.weight, reverse=True)[:3]
        reasoning = [
            f"Directional consensus selected {name} with support from {', '.join(supporters)}.",
            "Highest weighted agents: "
            + ", ".join(
                f"{item.vote.agent_id} ({item.weight:.2f})" for item in top_weights
            )
            + ".",
        ]
        if critiques:
            reasoning.append(
                "Critic loop logged: "
                + " ".join(critique.comment for critique in critiques)
            )
        return reasoning
