from collections import Counter

from app.schemas import AgentFinding, Recommendation


def clamp_score(value: int) -> int:
    return max(0, min(100, value))


def recommendation_scores(findings: list[AgentFinding], confidence_adjustment: int = 0) -> dict[Recommendation, int]:
    totals: dict[Recommendation, int] = {"Support": 0, "Modify": 0, "Delay": 0, "Reject": 0}
    counts: Counter[str] = Counter()
    for finding in findings:
        totals[finding.recommendation] += finding.confidence_score
        counts[finding.recommendation] += 1

    scores: dict[Recommendation, int] = {"Support": 0, "Modify": 0, "Delay": 0, "Reject": 0}
    for rec in scores:
        if counts[rec]:
            scores[rec] = clamp_score(round(totals[rec] / counts[rec]) + confidence_adjustment)
    return scores


def choose_recommendation(scores: dict[Recommendation, int]) -> Recommendation:
    return max(scores, key=scores.get)

