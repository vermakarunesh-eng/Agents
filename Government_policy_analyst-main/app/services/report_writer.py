import json
from pathlib import Path

from app.config import get_settings
from app.database import save_report_record
from app.schemas import PolicyReport


def build_memo(report: PolicyReport) -> str:
    evidence_lines = "\n".join(
        f"- {item.id}: {item.source_name} ({item.credibility_rating}/5) - {item.summary}" for item in report.evidence
    )
    finding_lines = "\n\n".join(
        "\n".join(
            [
                f"### {finding.agent_name}",
                finding.summary,
                *[f"- {point}" for point in finding.key_points],
                f"Recommendation: {finding.recommendation}; Confidence: {finding.confidence_score}/100",
            ]
        )
        for finding in report.findings
    )
    risk_lines = "\n".join(f"- {risk}" for finding in report.findings for risk in finding.risks)

    return f"""# Government Policy Analysis Memo

## Executive Summary
{report.input.title} in {report.input.jurisdiction} receives a consensus recommendation of **{report.consensus.recommendation}** with a directional confidence score of **{report.consensus.directional_confidence_score}/100**.

## Policy Context
Analysis depth: {report.input.analysis_depth}. The system reviewed submitted policy text and source metadata, then routed the issue through specialist policy agents.

## Key Evidence Reviewed
{evidence_lines}

## Specialist Agent Findings
{finding_lines}

## Critic Review
- Unsupported claims: {", ".join(report.critic.unsupported_claims) or "None identified."}
- Conflicts: {", ".join(report.critic.conflicts) or "No major directional conflict."}
- Missing evidence: {", ".join(report.critic.missing_evidence) or "No major gaps identified."}

## Consensus Recommendation
Recommendation: {report.consensus.recommendation}
Directional Confidence Score: {report.consensus.directional_confidence_score}

{report.consensus.reasoning}

## Stakeholder Impact
Review citizen access, business compliance burden, state/local delivery requirements, and effects on vulnerable groups before final approval.

## Fiscal Impact
Prepare budget notes separating setup cost, recurring cost, funding source, and sensitivity scenarios.

## Legal and Regulatory Risk
Confirm enabling authority, procedural requirements, rights impacts, and any conflicts with existing statutes or obligations.

## Implementation Feasibility
Use a phased rollout, clear ownership, service standards, monitoring indicators, and grievance mechanisms.

## Risks and Mitigations
{risk_lines}

## Open Questions
- What primary official documents, budget estimates, and consultation records should be added?
- Which agency owns implementation, audit, and public reporting?
- What metrics will determine whether the policy should continue, change, or stop?

## Evidence Log
{evidence_lines}
"""


def save_report(report: PolicyReport) -> tuple[Path, Path]:
    settings = get_settings()
    settings.reports_dir.mkdir(parents=True, exist_ok=True)
    markdown_path = settings.reports_dir / f"{report.id}.md"
    json_path = settings.reports_dir / f"{report.id}.json"
    markdown_path.write_text(report.memo_markdown, encoding="utf-8")
    json_path.write_text(json.dumps(report.model_dump(mode="json"), indent=2), encoding="utf-8")
    save_report_record(
        report.id,
        report.input.title,
        report.input.jurisdiction,
        report.created_at.isoformat(),
        str(markdown_path),
        str(json_path),
    )
    return markdown_path, json_path

