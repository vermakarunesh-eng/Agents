from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Action(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


@dataclass(frozen=True)
class Evidence:
    source: str
    summary: str
    strength: float


@dataclass(frozen=True)
class AgentVote:
    agent_id: str
    action: Action
    symbol: str
    confidence: float
    thesis: str
    evidence: tuple[Evidence, ...] = ()
    alternatives: tuple[str, ...] = ()


@dataclass(frozen=True)
class Critique:
    critic_id: str
    severity: float
    comment: str
    suggested_symbol: str | None = None


@dataclass(frozen=True)
class WeightedVote:
    vote: AgentVote
    weight: float
    components: dict[str, float]


@dataclass(frozen=True)
class TradeInstruction:
    action: Action
    symbol: str
    name: str
    confidence: float
    rationale: str


@dataclass(frozen=True)
class ConsensusDecision:
    primary: TradeInstruction
    exit_instruction: TradeInstruction | None
    directional_confidence_score: float
    consensus_reasoning: tuple[str, ...]
    evidence_used: tuple[Evidence, ...]
    alternatives_considered: tuple[str, ...]
    critiques: tuple[Critique, ...]
    weighted_votes: tuple[WeightedVote, ...]
    expected_return: float
    expected_drawdown: float
    forensic_log: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        def evidence_to_dict(item: Evidence) -> dict[str, Any]:
            return {
                "source": item.source,
                "summary": item.summary,
                "strength": round(item.strength, 4),
            }

        def instruction_to_dict(item: TradeInstruction | None) -> dict[str, Any] | None:
            if item is None:
                return None
            return {
                "action": item.action.value,
                "symbol": item.symbol,
                "name": item.name,
                "confidence": round(item.confidence, 4),
                "rationale": item.rationale,
            }

        return {
            "primary": instruction_to_dict(self.primary),
            "exit_instruction": instruction_to_dict(self.exit_instruction),
            "directional_confidence_score": round(
                self.directional_confidence_score, 4
            ),
            "consensus_reasoning": list(self.consensus_reasoning),
            "evidence_used": [evidence_to_dict(item) for item in self.evidence_used],
            "alternatives_considered": list(self.alternatives_considered),
            "critiques": [
                {
                    "critic_id": item.critic_id,
                    "severity": round(item.severity, 4),
                    "comment": item.comment,
                    "suggested_symbol": item.suggested_symbol,
                }
                for item in self.critiques
            ],
            "weighted_votes": [
                {
                    "agent_id": item.vote.agent_id,
                    "action": item.vote.action.value,
                    "symbol": item.vote.symbol,
                    "confidence": round(item.vote.confidence, 4),
                    "weight": round(item.weight, 4),
                    "components": {
                        key: round(value, 4)
                        for key, value in item.components.items()
                    },
                }
                for item in self.weighted_votes
            ],
            "expected_return": round(self.expected_return, 4),
            "expected_drawdown": round(self.expected_drawdown, 4),
            "forensic_log": self.forensic_log,
        }


@dataclass(frozen=True)
class MarketContext:
    as_of: str
    portfolio: dict[str, Any]
    candidates: dict[str, dict[str, Any]]
    macro: dict[str, float]
    reliability: dict[str, float] = field(default_factory=dict)
    directional_trust: dict[str, dict[str, float]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> MarketContext:
        return cls(
            as_of=str(payload.get("as_of", "")),
            portfolio=dict(payload.get("portfolio", {})),
            candidates=dict(payload.get("candidates", {})),
            macro=dict(payload.get("macro", {})),
            reliability=dict(payload.get("reliability", {})),
            directional_trust=dict(payload.get("directional_trust", {})),
        )
