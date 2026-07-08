from app.agents.base import BaseAgent
from app.schemas import AgentFinding, EvidenceItem, PolicyInput


class RiskAssessmentAgent(BaseAgent):
    name = "Risk Assessment Agent"

    def run(self, policy_input: PolicyInput, evidence: list[EvidenceItem]) -> AgentFinding:
        recommendation = "Delay" if not policy_input.policy_text and not policy_input.urls else "Modify"
        return self.finding(
            policy_input,
            evidence,
            summary="Aggregates political, legal, operational, reputational, market, and social risk.",
            key_points=[
                "Create risk register with owner, likelihood, impact, mitigation, and review date.",
                "Track early warning indicators after rollout.",
                "Use independent audit or third-party evaluation for high-impact programs.",
            ],
            risks=[
                "Low evidence depth increases false confidence.",
                "Public trust can weaken if objectives, eligibility, or enforcement are unclear.",
            ],
            confidence_score=62 if policy_input.policy_text or policy_input.urls else 45,
            recommendation=recommendation,
        )

