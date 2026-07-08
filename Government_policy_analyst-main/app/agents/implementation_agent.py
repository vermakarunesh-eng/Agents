from app.agents.base import BaseAgent
from app.schemas import AgentFinding, EvidenceItem, PolicyInput


class ImplementationAgent(BaseAgent):
    name = "Implementation Agent"

    def run(self, policy_input: PolicyInput, evidence: list[EvidenceItem]) -> AgentFinding:
        return self.finding(
            policy_input,
            evidence,
            summary="Assesses administrative capacity, sequencing, delivery channels, and operational bottlenecks.",
            key_points=[
                "Define accountable ministry, agency, state, or local implementation owners.",
                "Use phased rollout if delivery capacity or data infrastructure is uneven.",
                "Publish service standards, grievance channels, and monitoring indicators.",
            ],
            risks=[
                "Weak field capacity could delay benefits or enforcement.",
                "Fragmented data systems may reduce targeting and auditability.",
            ],
            confidence_score=66 if policy_input.policy_text else 50,
            recommendation="Modify",
        )

