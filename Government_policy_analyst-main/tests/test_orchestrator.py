from app.orchestrator import PolicyAnalysisOrchestrator
from app.schemas import PolicyInput


def test_orchestrator_creates_structured_report():
    report = PolicyAnalysisOrchestrator().analyze(
        PolicyInput(
            title="Data Protection Rule",
            jurisdiction="India",
            policy_text="Require consent records, grievance officer, and audit trails.",
            urls=["https://example.gov/rule"],
        ),
        persist=False,
    )
    assert report.consensus.recommendation in {"Support", "Modify", "Delay", "Reject"}
    assert len(report.findings) == 6
    assert report.evidence

