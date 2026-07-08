"""
Directional Consensus Agent B

Agent B models the committee participant shown in the directional-confidence
consensus workflow:

- moderate base confidence
- higher influence when it has historically disagreed with consensus and was
  later correct
- evidence-weighted directional recommendation across BUY / HOLD / SELL
- forensic trace explaining why the final direction was chosen

This file is self-contained and can be imported by a larger orchestrator or run
directly for a demo.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import argparse
import json
import math
from typing import Any, Iterable


class Direction(str, Enum):
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"


@dataclass(frozen=True)
class EvidenceSignal:
    name: str
    direction: Direction
    strength: float
    reliability: float
    notes: str = ""

    def __post_init__(self) -> None:
        _validate_unit_interval(self.strength, "strength")
        _validate_unit_interval(self.reliability, "reliability")


@dataclass(frozen=True)
class AgentBProfile:
    agent_id: str = "Agent B"
    base_confidence: float = 0.58
    disagreement_accuracy: float = 0.72
    recent_correctness: float = 0.66
    contrarian_bias_limit: float = 0.35
    min_action_confidence: float = 0.55

    def __post_init__(self) -> None:
        _validate_unit_interval(self.base_confidence, "base_confidence")
        _validate_unit_interval(self.disagreement_accuracy, "disagreement_accuracy")
        _validate_unit_interval(self.recent_correctness, "recent_correctness")
        _validate_unit_interval(self.contrarian_bias_limit, "contrarian_bias_limit")
        _validate_unit_interval(self.min_action_confidence, "min_action_confidence")


@dataclass(frozen=True)
class ConsensusContext:
    current_consensus: Direction
    consensus_confidence: float
    market_regime_risk: float
    peer_alignment: dict[str, Direction] = field(default_factory=dict)

    def __post_init__(self) -> None:
        _validate_unit_interval(self.consensus_confidence, "consensus_confidence")
        _validate_unit_interval(self.market_regime_risk, "market_regime_risk")


@dataclass(frozen=True)
class AgentBDecision:
    agent_id: str
    action: Direction
    confidence: float
    influence_weight: float
    directional_scores: dict[str, float]
    agrees_with_consensus: bool
    reasoning: list[str]
    evidence_used: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "action": self.action.value,
            "confidence": round(self.confidence, 4),
            "influence_weight": round(self.influence_weight, 4),
            "directional_scores": {
                key: round(value, 4) for key, value in self.directional_scores.items()
            },
            "agrees_with_consensus": self.agrees_with_consensus,
            "reasoning": self.reasoning,
            "evidence_used": self.evidence_used,
        }


class DirectionalConsensusAgentB:
    """
    Agent B converts evidence into a direction and an influence score.

    The important behavior is not merely what Agent B recommends; it is how much
    weight the committee should give that recommendation. This implementation
    increases Agent B's influence when it disagrees with the group and its
    disagreement track record is strong.
    """

    def __init__(self, profile: AgentBProfile | None = None) -> None:
        self.profile = profile or AgentBProfile()

    def decide(
        self,
        symbol: str,
        evidence: Iterable[EvidenceSignal],
        context: ConsensusContext,
    ) -> AgentBDecision:
        evidence_list = list(evidence)
        if not evidence_list:
            raise ValueError("Agent B needs at least one evidence signal.")

        raw_scores = {direction.value: 0.0 for direction in Direction}
        evidence_used: list[dict[str, Any]] = []

        for signal in evidence_list:
            weighted_signal = signal.strength * signal.reliability
            raw_scores[signal.direction.value] += weighted_signal
            evidence_used.append(
                {
                    "name": signal.name,
                    "direction": signal.direction.value,
                    "strength": signal.strength,
                    "reliability": signal.reliability,
                    "weighted_signal": round(weighted_signal, 4),
                    "notes": signal.notes,
                }
            )

        directional_scores = _softmax_scores(raw_scores)
        action = Direction(max(directional_scores, key=directional_scores.get))
        confidence = self._confidence(action, directional_scores, context)
        agrees_with_consensus = action == context.current_consensus
        influence_weight = self._influence_weight(
            confidence=confidence,
            agrees_with_consensus=agrees_with_consensus,
            context=context,
        )

        if confidence < self.profile.min_action_confidence:
            action = Direction.HOLD
            confidence = max(confidence, self.profile.min_action_confidence)
            agrees_with_consensus = action == context.current_consensus

        reasoning = self._reasoning(
            symbol=symbol,
            action=action,
            confidence=confidence,
            influence_weight=influence_weight,
            agrees_with_consensus=agrees_with_consensus,
            context=context,
            directional_scores=directional_scores,
        )

        return AgentBDecision(
            agent_id=self.profile.agent_id,
            action=action,
            confidence=confidence,
            influence_weight=influence_weight,
            directional_scores=directional_scores,
            agrees_with_consensus=agrees_with_consensus,
            reasoning=reasoning,
            evidence_used=evidence_used,
        )

    def _confidence(
        self,
        action: Direction,
        directional_scores: dict[str, float],
        context: ConsensusContext,
    ) -> float:
        winning_score = directional_scores[action.value]
        sorted_scores = sorted(directional_scores.values(), reverse=True)
        margin = sorted_scores[0] - sorted_scores[1]

        risk_penalty = context.market_regime_risk * 0.18
        confidence = (
            self.profile.base_confidence * 0.35
            + winning_score * 0.45
            + margin * 0.35
            + self.profile.recent_correctness * 0.15
            - risk_penalty
        )
        return _clamp(confidence, 0.0, 1.0)

    def _influence_weight(
        self,
        confidence: float,
        agrees_with_consensus: bool,
        context: ConsensusContext,
    ) -> float:
        historical_edge = (
            self.profile.disagreement_accuracy - context.consensus_confidence
        )
        contrarian_boost = _clamp(
            historical_edge,
            0.0,
            self.profile.contrarian_bias_limit,
        )

        if agrees_with_consensus:
            agreement_discount = 0.86
            return _clamp(confidence * agreement_discount, 0.0, 1.0)

        regime_discount = 1.0 - (context.market_regime_risk * 0.12)
        return _clamp((confidence + contrarian_boost) * regime_discount, 0.0, 1.0)

    def _reasoning(
        self,
        symbol: str,
        action: Direction,
        confidence: float,
        influence_weight: float,
        agrees_with_consensus: bool,
        context: ConsensusContext,
        directional_scores: dict[str, float],
    ) -> list[str]:
        stance = "agrees with" if agrees_with_consensus else "challenges"
        top_scores = ", ".join(
            f"{key}={value:.2f}"
            for key, value in sorted(
                directional_scores.items(), key=lambda item: item[1], reverse=True
            )
        )
        return [
            f"{self.profile.agent_id} recommends {action.value} for {symbol}.",
            f"The recommendation {stance} the current committee consensus "
            f"({context.current_consensus.value}).",
            f"Directional evidence distribution: {top_scores}.",
            f"Confidence is {confidence:.2f}; committee influence weight is "
            f"{influence_weight:.2f}.",
            "Historical disagreement accuracy is used only as an influence "
            "modifier, not as a substitute for current evidence.",
        ]


def load_evidence_from_json(path: str) -> tuple[str, list[EvidenceSignal], ConsensusContext]:
    with open(path, "r", encoding="utf-8") as file:
        payload = json.load(file)

    symbol = payload["symbol"]
    evidence = [
        EvidenceSignal(
            name=item["name"],
            direction=Direction(item["direction"].upper()),
            strength=float(item["strength"]),
            reliability=float(item["reliability"]),
            notes=item.get("notes", ""),
        )
        for item in payload["evidence"]
    ]
    context_payload = payload["context"]
    context = ConsensusContext(
        current_consensus=Direction(context_payload["current_consensus"].upper()),
        consensus_confidence=float(context_payload["consensus_confidence"]),
        market_regime_risk=float(context_payload["market_regime_risk"]),
        peer_alignment={
            key: Direction(value.upper())
            for key, value in context_payload.get("peer_alignment", {}).items()
        },
    )
    return symbol, evidence, context


def demo_payload() -> tuple[str, list[EvidenceSignal], ConsensusContext]:
    return (
        "NEXA",
        [
            EvidenceSignal(
                name="clean_energy_sentiment",
                direction=Direction.BUY,
                strength=0.74,
                reliability=0.68,
                notes="News and social sentiment improving for clean energy.",
            ),
            EvidenceSignal(
                name="technical_breakout",
                direction=Direction.BUY,
                strength=0.69,
                reliability=0.71,
                notes="Price broke above resistance with expanding volume.",
            ),
            EvidenceSignal(
                name="drawdown_risk",
                direction=Direction.SELL,
                strength=0.52,
                reliability=0.65,
                notes="Volatility remains above committee comfort band.",
            ),
            EvidenceSignal(
                name="valuation_stretch",
                direction=Direction.HOLD,
                strength=0.48,
                reliability=0.62,
                notes="Upside exists, but valuation is no longer cheap.",
            ),
        ],
        ConsensusContext(
            current_consensus=Direction.SELL,
            consensus_confidence=0.56,
            market_regime_risk=0.31,
            peer_alignment={"Agent A": Direction.SELL, "Agent D": Direction.HOLD},
        ),
    )


def _softmax_scores(raw_scores: dict[str, float]) -> dict[str, float]:
    max_score = max(raw_scores.values())
    exponents = {
        key: math.exp(value - max_score) for key, value in raw_scores.items()
    }
    total = sum(exponents.values())
    return {key: value / total for key, value in exponents.items()}


def _validate_unit_interval(value: float, name: str) -> None:
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be between 0.0 and 1.0.")


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Directional Consensus Agent B."
    )
    parser.add_argument(
        "--input",
        help="Optional JSON payload. If omitted, a NEXA demo case is used.",
    )
    args = parser.parse_args()

    if args.input:
        symbol, evidence, context = load_evidence_from_json(args.input)
    else:
        symbol, evidence, context = demo_payload()

    decision = DirectionalConsensusAgentB().decide(symbol, evidence, context)
    print(json.dumps(decision.to_dict(), indent=2))


if __name__ == "__main__":
    main()
