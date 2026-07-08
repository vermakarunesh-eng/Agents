from app.schemas import AgentFinding, EvidenceItem, PolicyInput, Recommendation


class BaseAgent:
    name = "Base Agent"
    default_recommendation: Recommendation = "Modify"

    def evidence_refs(self, evidence: list[EvidenceItem]) -> list[str]:
        return [item.id for item in evidence[:3]]

    def finding(
        self,
        policy_input: PolicyInput,
        evidence: list[EvidenceItem],
        summary: str,
        key_points: list[str],
        risks: list[str],
        confidence_score: int = 68,
        recommendation: Recommendation | None = None,
    ) -> AgentFinding:
        return AgentFinding(
            agent_name=self.name,
            summary=summary,
            key_points=key_points,
            risks=risks,
            confidence_score=confidence_score,
            evidence_refs=self.evidence_refs(evidence),
            recommendation=recommendation or self.default_recommendation,
        )

