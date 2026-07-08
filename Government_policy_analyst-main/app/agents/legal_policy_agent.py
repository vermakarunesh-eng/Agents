from app.agents.base import BaseAgent
from app.schemas import AgentFinding, EvidenceItem, PolicyInput


class LegalPolicyAgent(BaseAgent):
    name = "Legal Policy Agent"

    def run(self, policy_input: PolicyInput, evidence: list[EvidenceItem]) -> AgentFinding:
        return self.finding(
            policy_input,
            evidence,
            summary="Reviews statutory authority, procedural validity, and regulatory compliance exposure.",
            key_points=[
                f"Jurisdiction identified as {policy_input.jurisdiction}. Confirm the enabling act or executive authority.",
                "Check whether consultation, notice, rulemaking, or legislative approval is required.",
                "Flag rights, due process, privacy, equality, and federalism issues where applicable.",
            ],
            risks=[
                "Policy could face legal challenge if authority or consultation record is weak.",
                "Ambiguous definitions may create inconsistent implementation.",
            ],
            confidence_score=70 if policy_input.policy_text else 52,
            recommendation="Modify",
        )

