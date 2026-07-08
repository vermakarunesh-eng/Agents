import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.orchestrator import PolicyAnalysisOrchestrator
from app.schemas import PolicyInput


if __name__ == "__main__":
    sample_path = Path("app/data/samples/sample_policy_input.json")
    payload = json.loads(sample_path.read_text(encoding="utf-8"))
    report = PolicyAnalysisOrchestrator().analyze(PolicyInput(**payload))
    print(f"Created report: {report.id}")
    print(f"Recommendation: {report.consensus.recommendation}")
    print(f"Confidence: {report.consensus.directional_confidence_score}/100")
