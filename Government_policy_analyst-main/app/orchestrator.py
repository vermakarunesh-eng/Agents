from app.agents import (
    ConsensusAgent,
    CriticAgent,
    EvidenceAgent,
    FiscalImpactAgent,
    GeopoliticalAgent,
    ImplementationAgent,
    LegalPolicyAgent,
    PlannerAgent,
    RiskAssessmentAgent,
    StakeholderAgent,
)
from app.schemas import PolicyInput, PolicyReport
from app.services.report_writer import build_memo, save_report


class PolicyAnalysisOrchestrator:
    def __init__(self) -> None:
        self.planner = PlannerAgent()
        self.evidence_agent = EvidenceAgent()
        self.specialists = [
            LegalPolicyAgent(),
            FiscalImpactAgent(),
            ImplementationAgent(),
            StakeholderAgent(),
            GeopoliticalAgent(),
            RiskAssessmentAgent(),
        ]
        self.critic = CriticAgent()
        self.consensus = ConsensusAgent()

    def analyze(self, policy_input: PolicyInput, persist: bool = True) -> PolicyReport:
        self.planner.run(policy_input)
        evidence = self.evidence_agent.run(policy_input)
        findings = [agent.run(policy_input, evidence) for agent in self.specialists]
        critic = self.critic.run(policy_input, evidence, findings)
        consensus = self.consensus.run(findings, critic)
        report = PolicyReport(
            input=policy_input,
            evidence=evidence,
            findings=findings,
            critic=critic,
            consensus=consensus,
            memo_markdown="",
        )
        report.memo_markdown = build_memo(report)
        if persist:
            save_report(report)
        return report

