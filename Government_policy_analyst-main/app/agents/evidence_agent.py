from app.schemas import EvidenceItem, PolicyInput
from app.services.source_collector import collect_sources


class EvidenceAgent:
    def run(self, policy_input: PolicyInput) -> list[EvidenceItem]:
        return collect_sources(policy_input)

