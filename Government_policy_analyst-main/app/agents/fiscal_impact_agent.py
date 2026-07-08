from app.agents.base import BaseAgent
from app.schemas import AgentFinding, EvidenceItem, PolicyInput


class FiscalImpactAgent(BaseAgent):
    name = "Fiscal Impact Agent"

    def run(self, policy_input: PolicyInput, evidence: list[EvidenceItem]) -> AgentFinding:
        return self.finding(
            policy_input,
            evidence,
            summary="Estimates budgetary pressure, revenue implications, and public finance tradeoffs.",
            key_points=[
                "Separate one-time setup costs from recurring administrative and benefit costs.",
                "Identify funding source, fiscal year impact, and possible unfunded mandates.",
                "Require sensitivity estimates for low, central, and high adoption scenarios.",
            ],
            risks=[
                "Cost underestimation may weaken execution credibility.",
                "Revenue assumptions may be politically or economically fragile.",
            ],
            confidence_score=64 if policy_input.policy_text else 48,
            recommendation="Modify",
        )

