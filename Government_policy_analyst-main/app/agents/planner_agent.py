from app.schemas import PolicyInput


class PlannerAgent:
    domains = {
        "tax": "taxation",
        "budget": "economy",
        "health": "health",
        "school": "education",
        "education": "education",
        "climate": "environment",
        "defense": "defense",
        "trade": "trade",
        "data": "technology",
        "labor": "labor",
        "farm": "agriculture",
        "urban": "urban governance",
        "welfare": "welfare",
    }

    def run(self, policy_input: PolicyInput) -> dict:
        text = f"{policy_input.title} {policy_input.policy_text}".lower()
        domain = "other"
        for keyword, mapped_domain in self.domains.items():
            if keyword in text:
                domain = mapped_domain
                break

        return {
            "domain": domain,
            "selected_agents": [
                "LegalPolicyAgent",
                "FiscalImpactAgent",
                "ImplementationAgent",
                "StakeholderAgent",
                "GeopoliticalAgent",
                "RiskAssessmentAgent",
            ],
            "key_questions": [
                "What is the policy authority and legal basis?",
                "Who benefits, who bears cost, and who may be excluded?",
                "What fiscal, implementation, and political risks could alter outcomes?",
            ],
        }

