from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


Recommendation = Literal["Support", "Modify", "Delay", "Reject"]


class PolicyInput(BaseModel):
    title: str
    jurisdiction: str = "Unspecified"
    policy_text: str = ""
    urls: list[str] = Field(default_factory=list)
    analysis_depth: Literal["rapid", "standard", "deep"] = "standard"


class EvidenceItem(BaseModel):
    id: str = Field(default_factory=lambda: f"ev-{uuid4().hex[:8]}")
    source_name: str
    url: str | None = None
    date: str | None = None
    credibility_rating: int = Field(default=3, ge=1, le=5)
    summary: str


class AgentFinding(BaseModel):
    agent_name: str
    summary: str
    key_points: list[str]
    risks: list[str]
    confidence_score: int = Field(ge=0, le=100)
    evidence_refs: list[str] = Field(default_factory=list)
    recommendation: Recommendation


class CriticFinding(BaseModel):
    unsupported_claims: list[str]
    conflicts: list[str]
    missing_evidence: list[str]
    confidence_adjustment: int = Field(default=0, ge=-30, le=30)


class ConsensusDecision(BaseModel):
    recommendation: Recommendation
    directional_confidence_score: int = Field(ge=0, le=100)
    support_score: int = Field(ge=0, le=100)
    modify_score: int = Field(ge=0, le=100)
    delay_score: int = Field(ge=0, le=100)
    reject_score: int = Field(ge=0, le=100)
    reasoning: str


class PolicyReport(BaseModel):
    id: str = Field(default_factory=lambda: f"report-{uuid4().hex[:10]}")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    input: PolicyInput
    evidence: list[EvidenceItem]
    findings: list[AgentFinding]
    critic: CriticFinding
    consensus: ConsensusDecision
    memo_markdown: str
