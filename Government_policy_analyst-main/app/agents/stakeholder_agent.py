from app.agents.base import BaseAgent
from app.schemas import AgentFinding, EvidenceItem, PolicyInput


class StakeholderAgent(BaseAgent):
    name = "Stakeholder Agent"

    def run(self, policy_input: PolicyInput, evidence: list[EvidenceItem]) -> AgentFinding:
        return self.finding(
            policy_input,
            evidence,
            summary="Maps expected effects across citizens, firms, civil society, vulnerable groups, and subnational governments.",
            key_points=[
                "Identify direct beneficiaries, excluded groups, regulated entities, and compliance burden.",
                "Test whether vulnerable groups face access, documentation, language, or digital barriers.",
                "Plan consultation with affected communities and implementation partners.",
            ],
            risks=[
                "Benefits may be captured by better-informed or better-connected groups.",
                "Compliance burden may fall disproportionately on smaller organizations.",
            ],
            confidence_score=68 if policy_input.policy_text else 51,
            recommendation="Modify",
        )

