from __future__ import annotations

import json
import math
import random
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"
AGENTS_DIR = Path(r"C:\Heckathon2026\Agents")
CONSENSUS_DIR = AGENTS_DIR / "ConsensusEngine"

if str(CONSENSUS_DIR) not in sys.path:
    sys.path.insert(0, str(CONSENSUS_DIR))

from consensus_engine.engine import ConsensusEngine  # noqa: E402
from consensus_engine.models import MarketContext  # noqa: E402


STARTING_CASH = 10_000.0
MAX_LEVERAGE = 2.0
SESSION_STEPS = 18


BASE_CANDIDATES: dict[str, dict[str, Any]] = {
    "NVDA": {
        "name": "NVIDIA",
        "sector": "semiconductors",
        "price": 164.2,
        "price_momentum_20d": 0.19,
        "price_momentum_60d": 0.29,
        "rsi": 62,
        "macd": 0.12,
        "volume_surge": 0.46,
        "revenue_growth": 0.43,
        "earnings_growth": 0.38,
        "debt_to_equity": 0.22,
        "news_sentiment": 0.53,
        "social_sentiment": 0.41,
        "policy_tailwind": 0.21,
        "geopolitical_risk": 0.18,
        "volatility": 0.31,
        "max_drawdown": 0.15,
        "expected_return": 0.26,
    },
    "MSFT": {
        "name": "Microsoft",
        "sector": "mega-cap software",
        "price": 505.4,
        "price_momentum_20d": 0.08,
        "price_momentum_60d": 0.14,
        "rsi": 56,
        "macd": 0.05,
        "volume_surge": 0.12,
        "revenue_growth": 0.15,
        "earnings_growth": 0.17,
        "debt_to_equity": 0.3,
        "news_sentiment": 0.36,
        "social_sentiment": 0.23,
        "policy_tailwind": 0.1,
        "geopolitical_risk": 0.08,
        "volatility": 0.17,
        "max_drawdown": 0.08,
        "expected_return": 0.13,
    },
    "AAPL": {
        "name": "Apple",
        "sector": "consumer technology",
        "price": 231.9,
        "price_momentum_20d": 0.03,
        "price_momentum_60d": 0.05,
        "rsi": 51,
        "macd": 0.01,
        "volume_surge": 0.05,
        "revenue_growth": 0.04,
        "earnings_growth": 0.05,
        "debt_to_equity": 1.35,
        "news_sentiment": 0.16,
        "social_sentiment": 0.11,
        "policy_tailwind": -0.03,
        "geopolitical_risk": 0.2,
        "volatility": 0.19,
        "max_drawdown": 0.1,
        "expected_return": 0.08,
    },
    "AMZN": {
        "name": "Amazon",
        "sector": "cloud and retail",
        "price": 226.7,
        "price_momentum_20d": 0.1,
        "price_momentum_60d": 0.18,
        "rsi": 59,
        "macd": 0.06,
        "volume_surge": 0.19,
        "revenue_growth": 0.12,
        "earnings_growth": 0.22,
        "debt_to_equity": 0.61,
        "news_sentiment": 0.28,
        "social_sentiment": 0.2,
        "policy_tailwind": 0.04,
        "geopolitical_risk": 0.11,
        "volatility": 0.23,
        "max_drawdown": 0.11,
        "expected_return": 0.16,
    },
    "TSLA": {
        "name": "Tesla",
        "sector": "electric vehicles",
        "price": 314.8,
        "price_momentum_20d": -0.08,
        "price_momentum_60d": 0.04,
        "rsi": 67,
        "macd": -0.03,
        "volume_surge": 0.36,
        "revenue_growth": 0.07,
        "earnings_growth": -0.06,
        "debt_to_equity": 0.16,
        "news_sentiment": -0.12,
        "social_sentiment": 0.34,
        "policy_tailwind": 0.18,
        "geopolitical_risk": 0.24,
        "volatility": 0.42,
        "max_drawdown": 0.24,
        "expected_return": 0.11,
    },
    "JPM": {
        "name": "JPMorgan Chase",
        "sector": "financials",
        "price": 287.1,
        "price_momentum_20d": 0.06,
        "price_momentum_60d": 0.1,
        "rsi": 54,
        "macd": 0.04,
        "volume_surge": 0.09,
        "revenue_growth": 0.09,
        "earnings_growth": 0.13,
        "debt_to_equity": 1.18,
        "news_sentiment": 0.24,
        "social_sentiment": 0.08,
        "policy_tailwind": 0.12,
        "geopolitical_risk": 0.09,
        "volatility": 0.2,
        "max_drawdown": 0.09,
        "expected_return": 0.12,
    },
}


RELIABILITY = {
    "macro": 0.82,
    "fundamental": 0.87,
    "technical": 0.78,
    "sentiment": 0.7,
    "geopolitical": 0.71,
    "government_policy": 0.76,
    "risk": 0.84,
}


DIRECTIONAL_TRUST = {
    "macro": {"government_policy": 0.72, "fundamental": 0.66, "risk": 0.62},
    "fundamental": {"technical": 0.64, "sentiment": 0.57, "risk": 0.68},
    "technical": {"sentiment": 0.55, "risk": 0.51},
    "sentiment": {"technical": 0.54, "government_policy": 0.5},
    "geopolitical": {"risk": 0.73, "macro": 0.6},
    "government_policy": {"macro": 0.74, "fundamental": 0.62},
    "risk": {"geopolitical": 0.7, "fundamental": 0.64},
}


@dataclass
class Position:
    symbol: str
    name: str
    quantity: int
    average_price: float
    last_price: float

    @property
    def market_value(self) -> float:
        return self.quantity * self.last_price

    @property
    def unrealized_pl(self) -> float:
        return (self.last_price - self.average_price) * self.quantity


@dataclass
class TradingSession:
    cash: float = STARTING_CASH
    step: int = 0
    positions: dict[str, Position] = field(default_factory=dict)
    trade_history: list[dict[str, Any]] = field(default_factory=list)
    decision_log: list[dict[str, Any]] = field(default_factory=list)
    candidates: dict[str, dict[str, Any]] = field(
        default_factory=lambda: json.loads(json.dumps(BASE_CANDIDATES))
    )
    rng: random.Random = field(default_factory=lambda: random.Random(20260708))

    def portfolio_value(self) -> float:
        return self.cash + sum(position.market_value for position in self.positions.values())

    def gross_exposure(self) -> float:
        return sum(position.market_value for position in self.positions.values())

    def buying_power(self) -> float:
        return max(0.0, STARTING_CASH * MAX_LEVERAGE - self.gross_exposure())

    def portfolio_payload(self) -> dict[str, Any]:
        return {
            "cash": self.cash,
            "buying_power": self.buying_power(),
            "portfolio_value": self.portfolio_value(),
            "gross_exposure": self.gross_exposure(),
            "positions": {
                symbol: {
                    "name": item.name,
                    "quantity": item.quantity,
                    "average_price": item.average_price,
                    "last_price": item.last_price,
                    "market_value": item.market_value,
                    "unrealized_pl": item.unrealized_pl,
                    "sector": self.candidates[symbol]["sector"],
                }
                for symbol, item in self.positions.items()
            },
        }

    def market_context(self) -> MarketContext:
        return MarketContext.from_dict(
            {
                "as_of": datetime.now(timezone.utc).isoformat(),
                "portfolio": self.portfolio_payload(),
                "candidates": self.candidates,
                "macro": self.macro_regime(),
                "reliability": RELIABILITY,
                "directional_trust": DIRECTIONAL_TRUST,
            }
        )

    def macro_regime(self) -> dict[str, float]:
        pulse = math.sin((self.step + 2) / 3.0) * 0.03
        return {
            "gdp_trend": 0.024 + pulse,
            "inflation": 0.031,
            "interest_rate_bias": -0.008,
            "clean_energy_policy_strength": 0.18,
            "risk_regime": 0.34 + abs(pulse),
        }

    def advance_market(self) -> None:
        self.step += 1
        for symbol, item in self.candidates.items():
            momentum = float(item["price_momentum_20d"])
            sentiment = float(item["news_sentiment"])
            risk = float(item["volatility"])
            drift = 0.0009 + momentum * 0.006 + sentiment * 0.002
            shock = self.rng.gauss(0, 0.004 + risk * 0.006)
            new_price = max(5.0, float(item["price"]) * (1 + drift + shock))
            previous = float(item["price"])
            intraday_return = (new_price / previous) - 1
            item["price"] = round(new_price, 2)
            item["price_momentum_20d"] = clamp(momentum * 0.88 + intraday_return * 6, -0.35, 0.35)
            item["macd"] = clamp(float(item["macd"]) * 0.9 + intraday_return, -0.2, 0.2)
            item["rsi"] = clamp(float(item["rsi"]) + intraday_return * 180, 20, 82)
            item["volume_surge"] = clamp(float(item["volume_surge"]) * 0.92 + abs(shock) * 8, 0.02, 0.8)
            item["expected_return"] = clamp(
                float(item["expected_return"]) * 0.9 + item["price_momentum_20d"] * 0.6,
                -0.08,
                0.34,
            )
        for symbol, position in self.positions.items():
            position.last_price = float(self.candidates[symbol]["price"])

    def execute_decision(self, decision: dict[str, Any]) -> dict[str, Any]:
        primary = decision["primary"]
        action = primary["action"]
        symbol = primary["symbol"]
        confidence = float(primary["confidence"])
        current_position = self.positions.get(symbol)
        order_action = "WAIT"
        trade = None

        if decision.get("exit_instruction"):
            exit_symbol = decision["exit_instruction"]["symbol"]
            if exit_symbol in self.positions:
                trade = self.sell_all(exit_symbol, "SWITCH")
                order_action = "SWITCH"

        if action == "BUY" and confidence >= 0.54:
            trade = self.buy(symbol, confidence)
            if trade:
                order_action = "BUY" if order_action != "SWITCH" else "SWITCH"
        elif action == "SELL" and current_position:
            trade = self.sell_all(symbol, "SELL")
            order_action = "SELL"
        elif current_position:
            order_action = "HOLD"

        decision_record = {
            "step": self.step,
            "executed_action": order_action,
            "decision": decision,
            "portfolio": self.portfolio_payload(),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.decision_log.insert(0, decision_record)
        self.decision_log = self.decision_log[:50]
        return {"executed_action": order_action, "trade": trade, "decision_record": decision_record}

    def buy(self, symbol: str, confidence: float) -> dict[str, Any] | None:
        price = float(self.candidates[symbol]["price"])
        max_notional = min(self.buying_power(), self.portfolio_value() * (0.16 + confidence * 0.24))
        quantity = int(max_notional // price)
        if quantity <= 0:
            return None
        notional = quantity * price
        fees = trading_cost(notional)
        if notional + fees > self.cash + self.buying_power():
            return None
        existing = self.positions.get(symbol)
        if existing:
            total_quantity = existing.quantity + quantity
            existing.average_price = (
                existing.average_price * existing.quantity + notional
            ) / total_quantity
            existing.quantity = total_quantity
            existing.last_price = price
        else:
            self.positions[symbol] = Position(
                symbol=symbol,
                name=str(self.candidates[symbol]["name"]),
                quantity=quantity,
                average_price=price,
                last_price=price,
            )
        self.cash -= notional + fees
        trade = self.trade_payload("BUY", symbol, quantity, price, fees)
        self.trade_history.insert(0, trade)
        return trade

    def sell_all(self, symbol: str, action: str) -> dict[str, Any] | None:
        position = self.positions.pop(symbol, None)
        if not position:
            return None
        price = float(self.candidates[symbol]["price"])
        notional = position.quantity * price
        fees = trading_cost(notional)
        self.cash += notional - fees
        trade = self.trade_payload(action, symbol, position.quantity, price, fees)
        trade["realized_pl"] = (price - position.average_price) * position.quantity - fees
        self.trade_history.insert(0, trade)
        return trade

    def trade_payload(
        self, action: str, symbol: str, quantity: int, price: float, fees: float
    ) -> dict[str, Any]:
        return {
            "step": self.step,
            "time": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "symbol": symbol,
            "name": self.candidates[symbol]["name"],
            "quantity": quantity,
            "price": round(price, 2),
            "notional": round(quantity * price, 2),
            "costs": round(fees, 2),
        }


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def trading_cost(notional: float) -> float:
    commission = 0.0
    sec_fee = notional * 0.000008
    finra_taf = min(8.30, notional * 0.000166)
    spread_slippage = notional * 0.00025
    return commission + sec_fee + finra_taf + spread_slippage


SESSION = TradingSession()
ENGINE = ConsensusEngine()


def build_decision() -> dict[str, Any]:
    decision = ENGINE.decide(SESSION.market_context()).to_dict()
    decision["market"] = {
        "region": "US",
        "venue": "NASDAQ/NYSE paper market",
        "capital": STARTING_CASH,
        "max_leverage": MAX_LEVERAGE,
        "session_progress": SESSION.step / SESSION_STEPS,
        "remaining_steps": max(0, SESSION_STEPS - SESSION.step),
    }
    return decision


def snapshot() -> dict[str, Any]:
    decision = build_decision()
    return {
        "session": {
            "step": SESSION.step,
            "max_steps": SESSION_STEPS,
            "starting_cash": STARTING_CASH,
            "net_profit": SESSION.portfolio_value() - STARTING_CASH,
            "growth": (SESSION.portfolio_value() / STARTING_CASH) - 1,
        },
        "portfolio": SESSION.portfolio_payload(),
        "candidates": SESSION.candidates,
        "decision": decision,
        "trade_history": SESSION.trade_history[:20],
        "decision_log": SESSION.decision_log[:20],
    }


class AppHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path: str) -> str:
        parsed = urlparse(path)
        if parsed.path == "/":
            return str(STATIC_DIR / "index.html")
        return str(STATIC_DIR / parsed.path.lstrip("/"))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/snapshot":
            self.send_json(snapshot())
            return
        if parsed.path == "/api/decision":
            self.send_json(build_decision())
            return
        super().do_GET()

    def do_POST(self) -> None:
        global SESSION
        parsed = urlparse(self.path)
        if parsed.path == "/api/step":
            SESSION.advance_market()
            execution = SESSION.execute_decision(build_decision())
            payload = snapshot()
            payload["execution"] = execution
            self.send_json(payload)
            return
        if parsed.path == "/api/reset":
            SESSION = TradingSession()
            self.send_json(snapshot())
            return
        self.send_error(404)

    def send_json(self, payload: dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main() -> None:
    host = "127.0.0.1"
    port = 8765
    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f"Trading app running at http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
