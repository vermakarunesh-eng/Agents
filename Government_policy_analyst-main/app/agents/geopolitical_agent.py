from app.agents.base import BaseAgent
from app.schemas import AgentFinding, EvidenceItem, PolicyInput


class GeopoliticalAgent(BaseAgent):
    name = "Geopolitical Agent"

    def run(self, policy_input: PolicyInput, evidence: list[EvidenceItem]) -> AgentFinding:
        return self.finding(
            policy_input,
            evidence,
            summary="Checks cross-border, trade, sanctions, diplomatic, and international obligation implications.",
            key_points=[
                "Review compatibility with trade agreements and international commitments.",
                "Assess whether strategic sectors, data, defense, or energy interests are implicated.",
                "Identify likely reactions from major partners, investors, and multilateral bodies.",
            ],
            risks=[
                "Policy may create trade friction if discriminatory or opaque.",
                "International obligations may constrain policy design.",
            ],
            confidence_score=58,
            recommendation="Modify",
        )

