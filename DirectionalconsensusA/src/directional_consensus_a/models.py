from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Action = Literal["BUY", "HOLD", "SELL"]


@dataclass(frozen=True)
class StockCandidate:
    symbol: str
    name: str
    sector: str
    current_price: float
    revenue_growth_pct: float
    profit_margin_pct: float
    debt_to_equity: float
    rsi: float
    ema_signal: Literal["bullish", "neutral", "bearish"]
    volume_ratio: float
    news_sentiment: float
    social_sentiment: float
    macro_sensitivity: float
    volatility_pct: float
    max_drawdown_pct: float
    beta: float


@dataclass(frozen=True)
class Holding:
    symbol: str
    quantity: int
    average_price: float


@dataclass(frozen=True)
class PeerOpinion:
    agent_id: str
    symbol: str
    action: Action
    confidence: float
    historical_reliability: float
    rationale: str = ""


@dataclass(frozen=True)
class MarketContext:
    index_trend: Literal["bullish", "neutral", "bearish"]
    inflation_trend: Literal["rising", "stable", "falling"]
    interest_rate_outlook: Literal["hawkish", "neutral", "dovish"]
    risk_regime: Literal["risk_on", "balanced", "risk_off"]


@dataclass(frozen=True)
class MarketSnapshot:
    portfolio: list[Holding]
    candidates: list[StockCandidate]
    market_context: MarketContext
    peer_opinions: list[PeerOpinion] = field(default_factory=list)

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "MarketSnapshot":
        return cls(
            portfolio=[Holding(**item) for item in payload.get("portfolio", [])],
            candidates=[StockCandidate(**item) for item in payload["candidates"]],
            market_context=MarketContext(**payload["market_context"]),
            peer_opinions=[
                PeerOpinion(**item) for item in payload.get("peer_opinions", [])
            ],
        )


@dataclass(frozen=True)
class EvidenceScore:
    category: str
    score: float
    weight: float
    explanation: str


@dataclass(frozen=True)
class AgentDecision:
    agent_id: str
    symbol: str
    stock_name: str
    action: Action
    directional_score: float
    confidence: float
    expected_return_pct: float
    expected_drawdown_pct: float
    evidence: list[EvidenceScore]
    rationale: list[str]


@dataclass(frozen=True)
class CommitteeResult:
    selected: AgentDecision
    alternatives: list[AgentDecision]
    consensus_confidence: float
    peer_alignment: dict[str, float]
    forensic_log: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected": _decision_to_dict(self.selected),
            "alternatives": [_decision_to_dict(item) for item in self.alternatives],
            "consensus_confidence": round(self.consensus_confidence, 2),
            "peer_alignment": {
                key: round(value, 2) for key, value in self.peer_alignment.items()
            },
            "forensic_log": self.forensic_log,
        }


def _decision_to_dict(decision: AgentDecision) -> dict[str, Any]:
    return {
        "agent_id": decision.agent_id,
        "symbol": decision.symbol,
        "stock_name": decision.stock_name,
        "action": decision.action,
        "directional_score": round(decision.directional_score, 2),
        "confidence": round(decision.confidence, 2),
        "expected_return_pct": round(decision.expected_return_pct, 2),
        "expected_drawdown_pct": round(decision.expected_drawdown_pct, 2),
        "evidence": [
            {
                "category": item.category,
                "score": round(item.score, 2),
                "weight": item.weight,
                "explanation": item.explanation,
            }
            for item in decision.evidence
        ],
        "rationale": decision.rationale,
    }
