import json
from pathlib import Path

from fastapi import FastAPI, HTTPException

from app.database import list_report_records
from app.orchestrator import PolicyAnalysisOrchestrator
from app.schemas import PolicyInput, PolicyReport

app = FastAPI(title="Government Policy Agent", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze", response_model=PolicyReport)
def analyze(policy_input: PolicyInput) -> PolicyReport:
    return PolicyAnalysisOrchestrator().analyze(policy_input)


@app.get("/reports")
def reports() -> list[dict]:
    return list_report_records()


@app.get("/reports/{report_id}")
def report(report_id: str) -> dict:
    for record in list_report_records():
        if record["id"] == report_id:
            path = Path(record["json_path"])
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="Report not found")

