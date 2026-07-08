from __future__ import annotations

from .models import (
    AgentDecision,
    CommitteeResult,
    EvidenceScore,
    MarketContext,
    MarketSnapshot,
    PeerOpinion,
    StockCandidate,
)


class DirectionalConsensusAgentA:
    """Steady, evidence-first committee agent for directional consensus."""

    agent_id = "Agent A"

    def decide(self, snapshot: MarketSnapshot) -> CommitteeResult:
        decisions = [
            self._score_candidate(candidate, snapshot.market_context)
            for candidate in snapshot.candidates
        ]
        ranked = sorted(
            decisions,
            key=lambda item: (item.directional_score, item.confidence),
            reverse=True,
        )

        selected = self._apply_peer_consensus(ranked[0], snapshot.peer_opinions)
        alternatives = [self._apply_peer_consensus(item, snapshot.peer_opinions) for item in ranked[1:]]
        peer_alignment = self._peer_alignment(selected, snapshot.peer_opinions)
        consensus_confidence = self._consensus_confidence(selected, peer_alignment)

        forensic_log = [
            f"{self.agent_id} ranked {selected.symbol} highest with {selected.action} at {selected.confidence:.1f}% confidence.",
            f"Directional score combines evidence weights, then adjusts for peer reliability and alignment.",
        ]
        for evidence in selected.evidence:
            forensic_log.append(
                f"{selected.symbol} {evidence.category}: {evidence.explanation} ({evidence.score:+.1f})."
            )
        if peer_alignment:
            forensic_log.append(
                "Peer alignment: "
                + ", ".join(
                    f"{agent_id}={alignment:+.2f}"
                    for agent_id, alignment in peer_alignment.items()
                )
                + "."
            )

        return CommitteeResult(
            selected=selected,
            alternatives=alternatives,
            consensus_confidence=consensus_confidence,
            peer_alignment=peer_alignment,
            forensic_log=forensic_log,
        )

    def _score_candidate(
        self, candidate: StockCandidate, context: MarketContext
    ) -> AgentDecision:
        evidence = [
            self._fundamental_score(candidate),
            self._technical_score(candidate),
            self._sentiment_score(candidate),
            self._macro_score(candidate, context),
            self._risk_score(candidate, context),
        ]
        weighted_score = sum(item.score * item.weight for item in evidence)
        normalized_score = max(-100.0, min(100.0, weighted_score))
        confidence = min(99.0, 45.0 + abs(normalized_score) * 0.45)
        action = self._action_from_score(normalized_score)
        expected_return = normalized_score * 0.32
        expected_drawdown = max(1.0, candidate.max_drawdown_pct * (1.1 - confidence / 150.0))
        rationale = self._rationale(candidate, evidence, normalized_score)

        return AgentDecision(
            agent_id=self.agent_id,
            symbol=candidate.symbol,
            stock_name=candidate.name,
            action=action,
            directional_score=normalized_score,
            confidence=confidence,
            expected_return_pct=expected_return,
            expected_drawdown_pct=expected_drawdown,
            evidence=evidence,
            rationale=rationale,
        )

    def _fundamental_score(self, candidate: StockCandidate) -> EvidenceScore:
        growth = _scale(candidate.revenue_growth_pct, low=-10, high=30)
        margin = _scale(candidate.profit_margin_pct, low=0, high=25)
        leverage = -_scale(candidate.debt_to_equity, low=0.2, high=2.2)
        score = growth * 0.45 + margin * 0.35 + leverage * 0.20
        return EvidenceScore(
            category="fundamentals",
            score=score,
            weight=0.30,
            explanation=(
                f"revenue growth {candidate.revenue_growth_pct:.1f}%, "
                f"margin {candidate.profit_margin_pct:.1f}%, "
                f"debt/equity {candidate.debt_to_equity:.2f}"
            ),
        )

    def _technical_score(self, candidate: StockCandidate) -> EvidenceScore:
        rsi_score = 20.0 if 45 <= candidate.rsi <= 65 else -18.0
        if candidate.rsi < 35:
            rsi_score = 8.0
        if candidate.rsi > 72:
            rsi_score = -35.0

        ema_score = {"bullish": 42.0, "neutral": 0.0, "bearish": -42.0}[
            candidate.ema_signal
        ]
        volume_score = _scale(candidate.volume_ratio, low=0.6, high=1.8)
        score = rsi_score * 0.25 + ema_score * 0.50 + volume_score * 0.25
        return EvidenceScore(
            category="technicals",
            score=score,
            weight=0.22,
            explanation=(
                f"RSI {candidate.rsi:.1f}, EMA signal {candidate.ema_signal}, "
                f"volume ratio {candidate.volume_ratio:.2f}"
            ),
        )

    def _sentiment_score(self, candidate: StockCandidate) -> EvidenceScore:
        news = max(-100.0, min(100.0, candidate.news_sentiment * 100.0))
        social = max(-100.0, min(100.0, candidate.social_sentiment * 100.0))
        score = news * 0.65 + social * 0.35
        return EvidenceScore(
            category="sentiment",
            score=score,
            weight=0.16,
            explanation=(
                f"news sentiment {candidate.news_sentiment:+.2f}, "
                f"social sentiment {candidate.social_sentiment:+.2f}"
            ),
        )

    def _macro_score(
        self, candidate: StockCandidate, context: MarketContext
    ) -> EvidenceScore:
        trend = {"bullish": 28.0, "neutral": 0.0, "bearish": -32.0}[
            context.index_trend
        ]
        inflation = {"falling": 18.0, "stable": 4.0, "rising": -24.0}[
            context.inflation_trend
        ]
        rates = {"dovish": 20.0, "neutral": 2.0, "hawkish": -28.0}[
            context.interest_rate_outlook
        ]
        raw = trend * 0.35 + inflation * 0.25 + rates * 0.40
        score = raw * candidate.macro_sensitivity
        return EvidenceScore(
            category="macro",
            score=score,
            weight=0.14,
            explanation=(
                f"{context.index_trend} index, {context.inflation_trend} inflation, "
                f"{context.interest_rate_outlook} rates, sensitivity {candidate.macro_sensitivity:.2f}"
            ),
        )

    def _risk_score(
        self, candidate: StockCandidate, context: MarketContext
    ) -> EvidenceScore:
        volatility_penalty = _scale(candidate.volatility_pct, low=8, high=45)
        drawdown_penalty = _scale(candidate.max_drawdown_pct, low=4, high=35)
        beta_penalty = _scale(candidate.beta, low=0.6, high=1.8)
        regime_penalty = {"risk_on": 4.0, "balanced": -4.0, "risk_off": -24.0}[
            context.risk_regime
        ]
        score = (
            -volatility_penalty * 0.35
            - drawdown_penalty * 0.35
            - beta_penalty * 0.20
            + regime_penalty * 0.10
        )
        return EvidenceScore(
            category="risk",
            score=score,
            weight=0.18,
            explanation=(
                f"volatility {candidate.volatility_pct:.1f}%, drawdown {candidate.max_drawdown_pct:.1f}%, "
                f"beta {candidate.beta:.2f}, regime {context.risk_regime}"
            ),
        )

    def _apply_peer_consensus(
        self, decision: AgentDecision, opinions: list[PeerOpinion]
    ) -> AgentDecision:
        relevant = [item for item in opinions if item.symbol == decision.symbol]
        if not relevant:
            return decision

        peer_delta = 0.0
        for opinion in relevant:
            direction = {"BUY": 1.0, "HOLD": 0.0, "SELL": -1.0}[opinion.action]
            peer_delta += direction * opinion.confidence * opinion.historical_reliability
        peer_adjustment = peer_delta / max(1, len(relevant)) * 0.18
        adjusted_score = max(-100.0, min(100.0, decision.directional_score + peer_adjustment))
        adjusted_confidence = min(99.0, decision.confidence + abs(peer_adjustment) * 0.20)

        return AgentDecision(
            agent_id=decision.agent_id,
            symbol=decision.symbol,
            stock_name=decision.stock_name,
            action=self._action_from_score(adjusted_score),
            directional_score=adjusted_score,
            confidence=adjusted_confidence,
            expected_return_pct=adjusted_score * 0.32,
            expected_drawdown_pct=decision.expected_drawdown_pct,
            evidence=decision.evidence,
            rationale=decision.rationale
            + [f"Peer consensus adjusted score by {peer_adjustment:+.1f}."],
        )

    def _peer_alignment(
        self, decision: AgentDecision, opinions: list[PeerOpinion]
    ) -> dict[str, float]:
        alignment: dict[str, float] = {}
        target_direction = {"BUY": 1.0, "HOLD": 0.0, "SELL": -1.0}[decision.action]
        for opinion in opinions:
            if opinion.symbol != decision.symbol:
                continue
            peer_direction = {"BUY": 1.0, "HOLD": 0.0, "SELL": -1.0}[opinion.action]
            alignment[opinion.agent_id] = (
                target_direction * peer_direction * opinion.historical_reliability
            )
        return alignment

    def _consensus_confidence(
        self, decision: AgentDecision, alignment: dict[str, float]
    ) -> float:
        if not alignment:
            return decision.confidence
        average_alignment = sum(alignment.values()) / len(alignment)
        return max(0.0, min(100.0, decision.confidence + average_alignment * 12.0))

    def _action_from_score(self, score: float) -> str:
        if score >= 18.0:
            return "BUY"
        if score <= -18.0:
            return "SELL"
        return "HOLD"

    def _rationale(
        self,
        candidate: StockCandidate,
        evidence: list[EvidenceScore],
        normalized_score: float,
    ) -> list[str]:
        strongest = max(evidence, key=lambda item: item.score * item.weight)
        weakest = min(evidence, key=lambda item: item.score * item.weight)
        return [
            f"{candidate.symbol} net directional score is {normalized_score:+.1f}.",
            f"Strongest support comes from {strongest.category}.",
            f"Main constraint is {weakest.category}.",
        ]


def _scale(value: float, low: float, high: float) -> float:
    if high == low:
        return 0.0
    normalized = (value - low) / (high - low)
    return max(-100.0, min(100.0, normalized * 200.0 - 100.0))
