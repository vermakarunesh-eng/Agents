from __future__ import annotations

import argparse
import json
import mimetypes
from dataclasses import asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from algo_agent.agent import recommend
from algo_agent.policy import TradePolicy

from .broker import build_broker
from .execution import AgentExecutionEngine, ExecutionAuditLog
from .market_data import fetch_daily_bars, fetch_quote


ROOT = Path(__file__).resolve().parent
STATIC_ROOT = ROOT / "static"
AUDIT_LOG = ExecutionAuditLog(ROOT / "execution_audit.json")
EXECUTION_ENGINE = AgentExecutionEngine(AUDIT_LOG)


class TradingHandler(BaseHTTPRequestHandler):
    server_version = "AgentsTradingUI/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._send_file(STATIC_ROOT / "index.html")
            return
        if parsed.path.startswith("/static/"):
            self._send_file(STATIC_ROOT / parsed.path.removeprefix("/static/"))
            return
        if parsed.path == "/api/quote":
            self._handle_quote(parsed.query)
            return
        if parsed.path == "/api/recommendation":
            self._handle_recommendation(parsed.query)
            return
        if parsed.path == "/api/execution/status":
            self._send_json(build_broker().status())
            return
        if parsed.path == "/api/executions":
            self._send_json({"executions": AUDIT_LOG.list()})
            return
        self._send_json({"error": "Not found."}, HTTPStatus.NOT_FOUND)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/execute":
            self._handle_execute()
            return
        self._send_json({"error": "Not found."}, HTTPStatus.NOT_FOUND)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _handle_quote(self, query: str) -> None:
        params = parse_qs(query)
        symbol = _first(params, "symbol", "AAPL")
        quote = fetch_quote(symbol)
        self._send_json(quote.to_dict())

    def _handle_recommendation(self, query: str) -> None:
        params = parse_qs(query)
        symbol = _first(params, "symbol", "AAPL")
        source = _first(params, "source", "yahoo")
        horizon = _to_int(_first(params, "horizon", "5"), 5)
        policy = TradePolicy(
            capital=_to_float(_first(params, "capital", "100000"), 100000.0),
            account_risk_pct=_to_float(_first(params, "riskPct", "0.5"), 0.5),
            max_position_pct=_to_float(_first(params, "maxPositionPct", "8"), 8.0),
        )
        bars = fetch_daily_bars(symbol, preferred_source=source)
        recommendation = recommend(bars, symbol=symbol, horizon=horizon, policy=policy)
        latest = bars[-1]
        first = bars[max(0, len(bars) - 120)]
        recent_return = latest.close / first.close - 1.0 if first.close else 0.0
        feed_summary = {
            "status": "Live recommendation refreshed",
            "history_bars": len(bars),
            "start": first.date,
            "end": latest.date,
            "recent_return_pct": round(recent_return * 100.0, 2),
        }
        self._send_json(
            {
                "recommendation": recommendation.to_dict(),
                "feedSummary": feed_summary,
                "bars": [asdict(bar) for bar in bars[-120:]],
            }
        )

    def _handle_execute(self) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(content_length).decode("utf-8") or "{}")
            symbol = str(payload.get("symbol", ""))
            horizon = int(payload.get("horizon", 5))
            policy = TradePolicy(
                capital=float(payload.get("capital", 100000.0)),
                account_risk_pct=float(payload.get("riskPct", 0.5)),
                max_position_pct=float(payload.get("maxPositionPct", 8.0)),
            )
            bars = fetch_daily_bars(symbol, preferred_source=str(payload.get("source", "yahoo")))
            recommendation = recommend(bars, symbol=symbol, horizon=horizon, policy=policy)
            decision = EXECUTION_ENGINE.execute(
                recommendation,
                min_confidence=float(payload.get("minConfidence", 0.62)),
                cooldown_seconds=int(payload.get("cooldownSeconds", 900)),
            )
            status = HTTPStatus.CREATED if decision.submitted else HTTPStatus.ACCEPTED
            self._send_json(decision.to_dict(), status)
        except Exception as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)

    def _send_file(self, path: Path) -> None:
        safe_path = path.resolve()
        if not str(safe_path).startswith(str(STATIC_ROOT.resolve())) or not safe_path.exists():
            self._send_json({"error": "Not found."}, HTTPStatus.NOT_FOUND)
            return
        content = safe_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", mimetypes.guess_type(str(safe_path))[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, payload: dict, status: HTTPStatus = HTTPStatus.OK) -> None:
        content = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Agents trading dashboard.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    httpd = ThreadingHTTPServer((args.host, args.port), TradingHandler)
    print(f"Trading UI running at http://{args.host}:{args.port}")
    httpd.serve_forever()


def _first(params: dict[str, list[str]], name: str, default: str) -> str:
    values = params.get(name)
    return values[0] if values else default


def _to_float(value: str, default: float) -> float:
    try:
        return float(value)
    except ValueError:
        return default


def _to_int(value: str, default: int) -> int:
    try:
        return int(value)
    except ValueError:
        return default


if __name__ == "__main__":
    main()
