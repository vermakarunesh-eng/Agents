from app.schemas import AgentFinding, ConsensusDecision, CriticFinding
from app.services.scoring import choose_recommendation, recommendation_scores


class ConsensusAgent:
    def run(self, findings: list[AgentFinding], critic: CriticFinding) -> ConsensusDecision:
        scores = recommendation_scores(findings, critic.confidence_adjustment)
        recommendation = choose_recommendation(scores)
        directional_confidence = scores[recommendation]
        if directional_confidence == 0 and findings:
            directional_confidence = max(45, round(sum(f.confidence_score for f in findings) / len(findings)) - 15)

        return ConsensusDecision(
            recommendation=recommendation,
            directional_confidence_score=directional_confidence,
            support_score=scores["Support"],
            modify_score=scores["Modify"],
            delay_score=scores["Delay"],
            reject_score=scores["Reject"],
            reasoning=(
                f"The strongest weighted position is {recommendation}. "
                "The decision favors cautious improvement because most agents identify design, evidence, or execution gaps."
            ),
        )

