from app.schemas import EvidenceItem, PolicyInput


def collect_sources(policy_input: PolicyInput) -> list[EvidenceItem]:
    evidence: list[EvidenceItem] = []
    if policy_input.policy_text.strip():
        evidence.append(
            EvidenceItem(
                source_name="User-provided policy text",
                credibility_rating=4,
                summary=policy_input.policy_text.strip()[:500],
            )
        )

    for index, url in enumerate(policy_input.urls, start=1):
        if url.strip():
            evidence.append(
                EvidenceItem(
                    source_name=f"Submitted URL {index}",
                    url=url.strip(),
                    credibility_rating=3,
                    summary="URL submitted for review. Live retrieval is intentionally not assumed in local demo mode.",
                )
            )

    if not evidence:
        evidence.append(
            EvidenceItem(
                source_name="Analyst placeholder",
                credibility_rating=2,
                summary="No primary evidence supplied. Analysis should be treated as preliminary and evidence-limited.",
            )
        )
    return evidence

