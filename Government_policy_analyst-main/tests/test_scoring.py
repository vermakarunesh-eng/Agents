from app.schemas import AgentFinding
from app.services.scoring import choose_recommendation, recommendation_scores


def test_recommendation_scores_choose_highest_average():
    findings = [
        AgentFinding(
            agent_name="A",
            summary="s",
            key_points=[],
            risks=[],
            confidence_score=80,
            evidence_refs=[],
            recommendation="Support",
        ),
        AgentFinding(
            agent_name="B",
            summary="s",
            key_points=[],
            risks=[],
            confidence_score=65,
            evidence_refs=[],
            recommendation="Modify",
        ),
    ]
    scores = recommendation_scores(findings)
    assert scores["Support"] == 80
    assert choose_recommendation(scores) == "Support"


def test_adjustment_is_clamped():
    findings = [
        AgentFinding(
            agent_name="A",
            summary="s",
            key_points=[],
            risks=[],
            confidence_score=5,
            evidence_refs=[],
            recommendation="Delay",
        )
    ]
    assert recommendation_scores(findings, -30)["Delay"] == 0

