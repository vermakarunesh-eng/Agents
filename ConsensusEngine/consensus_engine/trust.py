from __future__ import annotations

from collections import defaultdict

from consensus_engine.models import AgentVote, MarketContext, WeightedVote


def directional_influence(agent_id: str, context: MarketContext) -> float:
    incoming: list[float] = []
    for source, targets in context.directional_trust.items():
        if source == agent_id:
            continue
        if agent_id in targets:
            incoming.append(float(targets[agent_id]))
    if not incoming:
        return 0.6
    return sum(incoming) / len(incoming)


def evidence_quality(vote: AgentVote) -> float:
    if not vote.evidence:
        return 0.5
    return sum(max(0.0, min(1.0, item.strength)) for item in vote.evidence) / len(
        vote.evidence
    )


def weight_votes(votes: list[AgentVote], context: MarketContext) -> list[WeightedVote]:
    weighted: list[WeightedVote] = []
    for vote in votes:
        reliability = float(context.reliability.get(vote.agent_id, 0.65))
        influence = directional_influence(vote.agent_id, context)
        quality = evidence_quality(vote)
        raw = vote.confidence * (0.42 + reliability * 0.28 + influence * 0.2 + quality * 0.1)
        weighted.append(
            WeightedVote(
                vote=vote,
                weight=raw,
                components={
                    "confidence": vote.confidence,
                    "reliability": reliability,
                    "directional_influence": influence,
                    "evidence_quality": quality,
                },
            )
        )
    return weighted


def score_by_symbol(weighted_votes: list[WeightedVote]) -> dict[str, float]:
    scores: dict[str, float] = defaultdict(float)
    for weighted in weighted_votes:
        multiplier = 1.0 if weighted.vote.action == "BUY" else 0.35
        scores[weighted.vote.symbol] += weighted.weight * multiplier
    return dict(scores)
