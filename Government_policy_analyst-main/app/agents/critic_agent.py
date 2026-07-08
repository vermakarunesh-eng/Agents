from app.schemas import AgentFinding, CriticFinding, EvidenceItem, PolicyInput


class CriticAgent:
    def run(self, policy_input: PolicyInput, evidence: list[EvidenceItem], findings: list[AgentFinding]) -> CriticFinding:
        missing = []
        if not policy_input.policy_text:
            missing.append("Primary policy text was not supplied.")
        if not policy_input.urls:
            missing.append("No official source URLs were supplied.")
        if all(item.credibility_rating < 4 for item in evidence):
            missing.append("Evidence set lacks high-credibility primary material.")

        recommendations = {finding.recommendation for finding in findings}
        conflicts = []
        if len(recommendations) > 1:
            conflicts.append(f"Agents disagree across recommendations: {', '.join(sorted(recommendations))}.")

        adjustment = -10 if missing else 0
        return CriticFinding(
            unsupported_claims=["Quantitative impacts need sourced estimates before public use."],
            conflicts=conflicts,
            missing_evidence=missing,
            confidence_adjustment=adjustment,
        )

