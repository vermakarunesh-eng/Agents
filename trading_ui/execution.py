from __future__ import annotations

import json
import threading
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from algo_agent.agent import Recommendation

from .broker import BrokerNotConfiguredError, BrokerOrderRequest, build_broker


@dataclass(frozen=True)
class ExecutionDecision:
    status: str
    reason: str
    submitted: bool
    order: dict | None
    recommendation: dict

    def to_dict(self) -> dict:
        return asdict(self)


class ExecutionAuditLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def list(self) -> list[dict]:
        with self._lock:
            return self._read()

    def append(self, event: dict) -> None:
        with self._lock:
            events = self._read()
            events.insert(0, event)
            self.path.write_text(json.dumps(events[:200], indent=2), encoding="utf-8")

    def latest_for_symbol(self, symbol: str) -> dict | None:
        symbol = symbol.upper()
        for event in self.list():
            if event.get("symbol") == symbol and event.get("submitted"):
                return event
        return None

    def _read(self) -> list[dict]:
        if not self.path.exists():
            return []
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            return payload if isinstance(payload, list) else []
        except json.JSONDecodeError:
            return []


class AgentExecutionEngine:
    def __init__(self, audit_log: ExecutionAuditLog) -> None:
        self.audit_log = audit_log

    def execute(
        self,
        recommendation: Recommendation,
        min_confidence: float = 0.62,
        cooldown_seconds: int = 900,
    ) -> ExecutionDecision:
        rec = recommendation.to_dict()
        symbol = recommendation.symbol.upper()

        block_reason = self._block_reason(recommendation, min_confidence, cooldown_seconds)
        if block_reason:
            decision = ExecutionDecision(
                status="BLOCKED",
                reason=block_reason,
                submitted=False,
                order=None,
                recommendation=rec,
            )
            self._log(symbol, decision)
            return decision

        side = "BUY" if recommendation.action == "BUY" else "SELL"
        order_request = BrokerOrderRequest(
            symbol=symbol,
            side=side,
            quantity=recommendation.shares,
            take_profit=recommendation.take_profit,
            stop_loss=recommendation.stop_loss,
        )
        broker = build_broker()
        try:
            result = broker.submit_order(order_request)
        except BrokerNotConfiguredError as exc:
            decision = ExecutionDecision(
                status="BLOCKED",
                reason=str(exc),
                submitted=False,
                order=None,
                recommendation=rec,
            )
            self._log(symbol, decision)
            return decision

        decision = ExecutionDecision(
            status="SUBMITTED",
            reason="Agent recommendation passed policy gates and broker accepted the order request.",
            submitted=True,
            order=result.to_dict(),
            recommendation=rec,
        )
        self._log(symbol, decision)
        return decision

    def _block_reason(
        self,
        recommendation: Recommendation,
        min_confidence: float,
        cooldown_seconds: int,
    ) -> str | None:
        if recommendation.action not in {"BUY", "SELL"}:
            return f"Agent action is {recommendation.action}; only BUY or SELL can be executed."
        if recommendation.review_status != "APPROVED_FOR_REVIEW":
            return f"Policy gates did not pass: {recommendation.review_status}."
        if recommendation.confidence < min_confidence:
            return f"Confidence {recommendation.confidence:.2%} is below required {min_confidence:.2%}."
        if recommendation.shares <= 0:
            return "Position sizing produced zero shares."

        latest = self.audit_log.latest_for_symbol(recommendation.symbol)
        if latest:
            age = time.time() - float(latest.get("timestamp", 0))
            if age < cooldown_seconds:
                return f"Cooldown active for {recommendation.symbol}; last submitted order was {int(age)} seconds ago."
        return None

    def _log(self, symbol: str, decision: ExecutionDecision) -> None:
        payload = decision.to_dict()
        payload["timestamp"] = time.time()
        payload["created_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
        payload["symbol"] = symbol
        self.audit_log.append(payload)
