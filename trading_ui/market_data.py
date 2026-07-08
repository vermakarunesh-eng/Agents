from __future__ import annotations

import csv
import json
import time
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from io import StringIO

from algo_agent.data import PriceBar


@dataclass(frozen=True)
class Quote:
    symbol: str
    price: float
    previous_close: float
    change: float
    change_pct: float
    currency: str
    market_state: str
    regular_market_time: str | None
    source: str
    points: list[dict[str, float | int | str]]

    def to_dict(self) -> dict:
        return asdict(self)


def fetch_quote(symbol: str) -> Quote:
    symbol = _normalize_symbol(symbol)
    try:
        return _fetch_yahoo_quote(symbol)
    except Exception:
        bars = fetch_daily_bars(symbol, preferred_source="stooq")
        latest = bars[-1]
        previous = bars[-2]
        change = latest.close - previous.close
        return Quote(
            symbol=symbol.upper(),
            price=round(latest.close, 4),
            previous_close=round(previous.close, 4),
            change=round(change, 4),
            change_pct=round(change / previous.close * 100.0, 4) if previous.close else 0.0,
            currency="",
            market_state="DELAYED_DAILY",
            regular_market_time=latest.date,
            source="stooq",
            points=[{"time": bar.date, "close": bar.close, "volume": bar.volume} for bar in bars[-80:]],
        )


def fetch_daily_bars(symbol: str, preferred_source: str = "yahoo") -> list[PriceBar]:
    symbol = _normalize_symbol(symbol)
    if preferred_source == "demo":
        from algo_agent.data import generate_demo_prices

        return generate_demo_prices()

    loaders = [_fetch_yahoo_daily_bars, _fetch_stooq_daily_bars]
    if preferred_source == "stooq":
        loaders.reverse()

    errors: list[str] = []
    for loader in loaders:
        try:
            bars = loader(symbol)
            if len(bars) >= 80:
                return bars
        except Exception as exc:
            errors.append(f"{loader.__name__}: {exc}")
    raise RuntimeError("Could not load enough market history. " + " | ".join(errors))


def _fetch_yahoo_quote(symbol: str) -> Quote:
    payload = _fetch_yahoo_chart(symbol, range_value="1d", interval="1m")
    result = payload["chart"]["result"][0]
    meta = result["meta"]
    timestamps = result.get("timestamp") or []
    quote = result["indicators"]["quote"][0]
    closes = quote.get("close") or []
    volumes = quote.get("volume") or []

    points = []
    for timestamp, close, volume in zip(timestamps, closes, volumes):
        if close is None:
            continue
        points.append({"time": int(timestamp), "close": round(float(close), 4), "volume": int(volume or 0)})

    price = float(meta.get("regularMarketPrice") or points[-1]["close"])
    previous = float(meta.get("previousClose") or meta.get("chartPreviousClose") or price)
    change = price - previous
    market_time = meta.get("regularMarketTime")
    return Quote(
        symbol=str(meta.get("symbol") or symbol).upper(),
        price=round(price, 4),
        previous_close=round(previous, 4),
        change=round(change, 4),
        change_pct=round(change / previous * 100.0, 4) if previous else 0.0,
        currency=str(meta.get("currency") or ""),
        market_state=str(meta.get("marketState") or "UNKNOWN"),
        regular_market_time=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(market_time))
        if isinstance(market_time, int)
        else None,
        source="yahoo",
        points=points[-240:],
    )


def _fetch_yahoo_daily_bars(symbol: str) -> list[PriceBar]:
    payload = _fetch_yahoo_chart(symbol, range_value="2y", interval="1d")
    result = payload["chart"]["result"][0]
    timestamps = result.get("timestamp") or []
    quote = result["indicators"]["quote"][0]
    bars: list[PriceBar] = []
    for timestamp, open_, high, low, close, volume in zip(
        timestamps,
        quote.get("open") or [],
        quote.get("high") or [],
        quote.get("low") or [],
        quote.get("close") or [],
        quote.get("volume") or [],
    ):
        if None in (open_, high, low, close):
            continue
        bars.append(
            PriceBar(
                date=time.strftime("%Y-%m-%d", time.localtime(int(timestamp))),
                open=float(open_),
                high=float(high),
                low=float(low),
                close=float(close),
                volume=float(volume or 0),
            )
        )
    return bars


def _fetch_yahoo_chart(symbol: str, range_value: str, interval: str) -> dict:
    query = urllib.parse.urlencode({"range": range_value, "interval": interval, "includePrePost": "false"})
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?{query}"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=15) as response:
        payload = json.loads(response.read().decode("utf-8"))
    error = payload.get("chart", {}).get("error")
    if error:
        raise RuntimeError(str(error))
    return payload


def _fetch_stooq_daily_bars(symbol: str) -> list[PriceBar]:
    query = urllib.parse.urlencode({"s": symbol.lower(), "i": "d"})
    url = f"https://stooq.com/q/d/l/?{query}"
    with urllib.request.urlopen(url, timeout=15) as response:
        content = response.read().decode("utf-8")
    reader = csv.DictReader(StringIO(content))
    if not reader.fieldnames or "Date" not in reader.fieldnames:
        raise RuntimeError("Stooq returned an unexpected response.")
    bars: list[PriceBar] = []
    for row in reader:
        try:
            bars.append(
                PriceBar(
                    date=row["Date"],
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=float(row["Volume"]),
                )
            )
        except (KeyError, TypeError, ValueError):
            continue
    bars.sort(key=lambda bar: bar.date)
    return bars


def _normalize_symbol(symbol: str) -> str:
    cleaned = symbol.strip().upper()
    if not cleaned:
        raise ValueError("Symbol is required.")
    return cleaned
