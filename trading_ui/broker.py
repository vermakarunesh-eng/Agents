from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class BrokerOrderRequest:
    symbol: str
    side: str
    quantity: int
    order_type: str = "market"
    time_in_force: str = "day"
    take_profit: float | None = None
    stop_loss: float | None = None


@dataclass(frozen=True)
class BrokerOrderResult:
    broker: str
    status: str
    order_id: str | None
    raw: dict

    def to_dict(self) -> dict:
        return asdict(self)


class BrokerNotConfiguredError(RuntimeError):
    pass


class AlpacaBroker:
    def __init__(
        self,
        key_id: str | None = None,
        secret_key: str | None = None,
        base_url: str | None = None,
        live_enabled: bool | None = None,
    ) -> None:
        self.key_id = key_id or os.getenv("ALPACA_KEY_ID")
        self.secret_key = secret_key or os.getenv("ALPACA_SECRET_KEY")
        self.base_url = (base_url or os.getenv("ALPACA_BASE_URL") or "").rstrip("/")
        self.live_enabled = _env_bool("ALGO_LIVE_TRADING_ENABLED") if live_enabled is None else live_enabled

    def status(self) -> dict:
        return {
            "broker": "alpaca",
            "configured": bool(self.key_id and self.secret_key and self.base_url),
            "live_enabled": self.live_enabled,
            "base_url": _redact_base_url(self.base_url),
        }

    def submit_order(self, order: BrokerOrderRequest) -> BrokerOrderResult:
        if not self.live_enabled:
            raise BrokerNotConfiguredError("Live trading is disabled. Set ALGO_LIVE_TRADING_ENABLED=true.")
        if not self.key_id or not self.secret_key or not self.base_url:
            raise BrokerNotConfiguredError("Alpaca broker is not configured. Set ALPACA_KEY_ID, ALPACA_SECRET_KEY, and ALPACA_BASE_URL.")

        payload: dict[str, object] = {
            "symbol": order.symbol.upper(),
            "qty": str(order.quantity),
            "side": order.side.lower(),
            "type": order.order_type,
            "time_in_force": order.time_in_force,
        }
        if order.take_profit is not None and order.stop_loss is not None:
            payload["order_class"] = "bracket"
            payload["take_profit"] = {"limit_price": str(round(order.take_profit, 2))}
            payload["stop_loss"] = {"stop_price": str(round(order.stop_loss, 2))}

        request = urllib.request.Request(
            f"{self.base_url}/v2/orders",
            data=json.dumps(payload).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "APCA-API-KEY-ID": self.key_id,
                "APCA-API-SECRET-KEY": self.secret_key,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            try:
                error_payload = json.loads(body)
            except json.JSONDecodeError:
                error_payload = {"message": body}
            raise RuntimeError(f"Broker rejected order: {error_payload}") from exc

        return BrokerOrderResult(
            broker="alpaca",
            status=str(raw.get("status") or "submitted"),
            order_id=str(raw.get("id")) if raw.get("id") else None,
            raw=raw,
        )


def build_broker() -> AlpacaBroker:
    return AlpacaBroker()


def _env_bool(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _redact_base_url(value: str) -> str:
    if not value:
        return ""
    return value.replace("https://", "").replace("http://", "")
