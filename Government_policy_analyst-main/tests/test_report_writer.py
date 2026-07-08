from app.orchestrator import PolicyAnalysisOrchestrator
from app.schemas import PolicyInput


def test_report_contains_required_sections():
    report = PolicyAnalysisOrchestrator().analyze(
        PolicyInput(title="Health Program", jurisdiction="Testland", policy_text="Expand primary care."),
        persist=False,
    )
    assert "# Government Policy Analysis Memo" in report.memo_markdown
    assert "## Consensus Recommendation" in report.memo_markdown
    assert "## Evidence Log" in report.memo_markdown

