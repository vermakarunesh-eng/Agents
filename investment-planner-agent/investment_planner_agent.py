from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol


Action = str


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def normalize_score(value: float) -> float:
    return clamp(value, -1.0, 1.0)


@dataclass(frozen=True)
class Evidence:
    source: str
    symbol: str
    action: Action
    confidence: float
    directional_score: float
    rationale: str
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AgentProfile:
    name: str
    role: str
    historical_reliability: float
    contrarian_value: float


class AnalystAgent(Protocol):
    profile: AgentProfile

    def analyze(self, request: dict[str, Any], candidate: dict[str, Any]) -> Evidence:
        ...


class MacroEconomistAgent:
    profile = AgentProfile("MacroEconomist", "GDP, inflation, rates, liquidity", 0.72, 0.18)

    def analyze(self, request: dict[str, Any], candidate: dict[str, Any]) -> Evidence:
        macro = request["macro"]
        rate_penalty = (macro["interest_rate_pct"] - 5.5) * 0.11
        inflation_penalty = max(0, macro["inflation_pct"] - 4.0) * 0.08
        growth_boost = (macro["gdp_growth_pct"] - 5.5) * 0.13
        policy_boost = candidate["policy_tailwind"] * 0.45
        score = normalize_score(growth_boost + policy_boost - rate_penalty - inflation_penalty)
        return Evidence(
            self.profile.name,
            candidate["symbol"],
            action_from_score(score),
            confidence=0.62 + abs(score) * 0.22,
            directional_score=score,
            rationale="Macro backdrop favors policy-supported growth but discounts rate and inflation pressure.",
            metrics=macro,
        )


class FundamentalAnalystAgent:
    profile = AgentProfile("FundamentalAnalyst", "Valuation, growth, balance sheet", 0.78, 0.12)

    def analyze(self, request: dict[str, Any], candidate: dict[str, Any]) -> Evidence:
        growth = (candidate["revenue_growth_pct"] + candidate["profit_growth_pct"]) / 2
        valuation_penalty = max(0, candidate["pe"] - 35) / 70
        leverage_penalty = max(0, candidate["debt_to_equity"] - 1.2) / 2.5
        score = normalize_score((growth - 12) / 24 - valuation_penalty - leverage_penalty)
        return Evidence(
            self.profile.name,
            candidate["symbol"],
            action_from_score(score),
            confidence=0.58 + abs(score) * 0.28,
            directional_score=score,
            rationale="Compares growth quality against valuation and balance-sheet risk.",
            metrics={
                "pe": candidate["pe"],
                "revenue_growth_pct": candidate["revenue_growth_pct"],
                "profit_growth_pct": candidate["profit_growth_pct"],
                "debt_to_equity": candidate["debt_to_equity"],
            },
        )


class TechnicalAnalystAgent:
    profile = AgentProfile("TechnicalAnalyst", "RSI, MACD, volume", 0.64, 0.22)

    def analyze(self, request: dict[str, Any], candidate: dict[str, Any]) -> Evidence:
        rsi = candidate["rsi"]
        rsi_score = 0.35 if 45 <= rsi <= 63 else -0.45 if rsi >= 75 else -0.1 if rsi <= 35 else 0.05
        macd_score = {"bullish": 0.35, "neutral": 0.0, "bearish": -0.35}[candidate["macd_signal"]]
        volume_score = {"rising": 0.2, "stable": 0.04, "fading": -0.18}[candidate["volume_trend"]]
        score = normalize_score(rsi_score + macd_score + volume_score)
        return Evidence(
            self.profile.name,
            candidate["symbol"],
            action_from_score(score),
            confidence=0.55 + abs(score) * 0.32,
            directional_score=score,
            rationale="Reads near-term momentum using RSI, MACD, and volume confirmation.",
            metrics={"rsi": rsi, "macd_signal": candidate["macd_signal"], "volume_trend": candidate["volume_trend"]},
        )


class SentimentAnalystAgent:
    profile = AgentProfile("SentimentAnalyst", "News and social sentiment", 0.59, 0.25)

    def analyze(self, request: dict[str, Any], candidate: dict[str, Any]) -> Evidence:
        score = normalize_score(candidate["news_sentiment"] * 0.72 + candidate["social_sentiment"] * 0.28)
        return Evidence(
            self.profile.name,
            candidate["symbol"],
            action_from_score(score),
            confidence=0.50 + abs(score) * 0.30,
            directional_score=score,
            rationale="Aggregates news and social direction while keeping confidence modest.",
            metrics={"news_sentiment": candidate["news_sentiment"], "social_sentiment": candidate["social_sentiment"]},
        )


class PolicyAnalystAgent:
    profile = AgentProfile("PolicyAnalyst", "RBI, SEBI, taxation, industrial policy", 0.69, 0.16)

    def analyze(self, request: dict[str, Any], candidate: dict[str, Any]) -> Evidence:
        score = normalize_score(candidate["policy_tailwind"] - 0.12)
        return Evidence(
            self.profile.name,
            candidate["symbol"],
            action_from_score(score),
            confidence=0.57 + abs(score) * 0.30,
            directional_score=score,
            rationale="Scores sector and company benefit from current policy tailwinds.",
            metrics={"policy_tailwind": candidate["policy_tailwind"]},
        )


class GeopoliticalAnalystAgent:
    profile = AgentProfile("GeopoliticalAnalyst", "Supply chain, sanctions, trade risk", 0.63, 0.20)

    def analyze(self, request: dict[str, Any], candidate: dict[str, Any]) -> Evidence:
        score = normalize_score(0.18 - candidate["geopolitical_risk"])
        return Evidence(
            self.profile.name,
            candidate["symbol"],
            action_from_score(score),
            confidence=0.54 + abs(score) * 0.30,
            directional_score=score,
            rationale="Penalizes higher supply-chain, trade, and cross-border risk.",
            metrics={"geopolitical_risk": candidate["geopolitical_risk"]},
        )


class RiskAssessmentAgent:
    profile = AgentProfile("RiskAssessment", "Volatility, beta proxy, drawdown", 0.81, 0.10)

    def analyze(self, request: dict[str, Any], candidate: dict[str, Any]) -> Evidence:
        profile = request["investor_profile"]
        vol_penalty = max(0, candidate["volatility_pct"] - 22) / 35
        dd_penalty = max(0, candidate["max_drawdown_pct"] - profile["max_drawdown_pct"]) / 22
        score = normalize_score(0.2 - vol_penalty - dd_penalty)
        return Evidence(
            self.profile.name,
            candidate["symbol"],
            action_from_score(score),
            confidence=0.66 + abs(score) * 0.26,
            directional_score=score,
            rationale="Checks whether volatility and expected drawdown fit the investor mandate.",
            metrics={"volatility_pct": candidate["volatility_pct"], "max_drawdown_pct": candidate["max_drawdown_pct"]},
        )


class OpportunityCriticAgent:
    profile = AgentProfile("OpportunityCritic", "Searches for better opportunity cost", 0.70, 0.35)

    def analyze(self, request: dict[str, Any], candidate: dict[str, Any]) -> Evidence:
        peers = [c for c in request["candidates"] if c["symbol"] != candidate["symbol"]]
        best_peer_growth = max((p["profit_growth_pct"] - p["debt_to_equity"] * 4 for p in peers), default=0)
        current_quality = candidate["profit_growth_pct"] - candidate["debt_to_equity"] * 4
        opportunity_gap = best_peer_growth - current_quality
        score = normalize_score(-opportunity_gap / 30)
        return Evidence(
            self.profile.name,
            candidate["symbol"],
            action_from_score(score),
            confidence=0.56 + abs(score) * 0.28,
            directional_score=score,
            rationale="Challenges the proposed allocation against stronger available alternatives.",
            metrics={"opportunity_gap": round(opportunity_gap, 2)},
        )


def action_from_score(score: float) -> Action:
    if score >= 0.28:
        return "BUY"
    if score <= -0.28:
        return "SELL"
    return "HOLD"


class InvestmentPlannerAgent:
    def __init__(self) -> None:
        self.specialists: list[AnalystAgent] = [
            MacroEconomistAgent(),
            FundamentalAnalystAgent(),
            TechnicalAnalystAgent(),
            SentimentAnalystAgent(),
            PolicyAnalystAgent(),
            GeopoliticalAnalystAgent(),
            RiskAssessmentAgent(),
            OpportunityCriticAgent(),
        ]

    def select_agents(self, request: dict[str, Any]) -> list[AnalystAgent]:
        risk = request["investor_profile"]["risk_tolerance"].lower()
        horizon = request["investor_profile"]["time_horizon_months"]
        selected: list[AnalystAgent] = []
        for agent in self.specialists:
            if risk in {"conservative", "moderate"}:
                selected.append(agent)
            elif agent.profile.name != "RiskAssessment" or horizon < 18:
                selected.append(agent)
            else:
                selected.append(agent)
        return selected

    def run(self, request: dict[str, Any]) -> dict[str, Any]:
        selected = self.select_agents(request)
        evidence: list[Evidence] = []
        for candidate in request["candidates"]:
            for agent in selected:
                evidence.append(agent.analyze(request, candidate))

        consensus = DirectionalTrustAwareConsensus().fuse(evidence, selected)
        allocation = PortfolioExecutionAgent().allocate(request, consensus)
        return ForensicLogger().render(request, selected, evidence, consensus, allocation)


class DirectionalTrustAwareConsensus:
    def fuse(self, evidence: list[Evidence], agents: list[AnalystAgent]) -> dict[str, Any]:
        profiles = {agent.profile.name: agent.profile for agent in agents}
        by_symbol: dict[str, list[Evidence]] = {}
        for item in evidence:
            by_symbol.setdefault(item.symbol, []).append(item)

        ranked: list[dict[str, Any]] = []
        for symbol, items in by_symbol.items():
            weighted_sum = 0.0
            total_weight = 0.0
            action_votes = {"BUY": 0.0, "HOLD": 0.0, "SELL": 0.0}
            for item in items:
                profile = profiles[item.source]
                directional_weight = item.confidence * profile.historical_reliability
                if item.action != "HOLD":
                    directional_weight *= 1 + profile.contrarian_value * 0.25
                weighted_sum += item.directional_score * directional_weight
                total_weight += directional_weight
                action_votes[item.action] += directional_weight

            score = weighted_sum / total_weight if total_weight else 0.0
            disagreement = self._disagreement(items)
            confidence = clamp((abs(score) * 0.70 + (1 - disagreement) * 0.30) * 100, 0, 100)
            ranked.append(
                {
                    "symbol": symbol,
                    "action": action_from_score(score),
                    "directional_score": round(score, 3),
                    "directional_confidence_pct": round(confidence, 1),
                    "vote_weight": {k: round(v, 3) for k, v in action_votes.items()},
                    "disagreement_index": round(disagreement, 3),
                    "top_evidence": self._top_evidence(items),
                }
            )

        ranked.sort(key=lambda item: (item["action"] == "BUY", item["directional_confidence_pct"], item["directional_score"]), reverse=True)
        return {"ranked_actions": ranked, "committee_confidence_pct": self._committee_confidence(ranked)}

    def _disagreement(self, items: list[Evidence]) -> float:
        if not items:
            return 0.0
        mean = sum(item.directional_score for item in items) / len(items)
        variance = sum((item.directional_score - mean) ** 2 for item in items) / len(items)
        return clamp(math.sqrt(variance), 0.0, 1.0)

    def _top_evidence(self, items: list[Evidence]) -> list[dict[str, Any]]:
        strongest = sorted(items, key=lambda item: item.confidence * abs(item.directional_score), reverse=True)[:3]
        return [
            {
                "agent": item.source,
                "action": item.action,
                "confidence": round(item.confidence, 3),
                "rationale": item.rationale,
                "metrics": item.metrics,
            }
            for item in strongest
        ]

    def _committee_confidence(self, ranked: list[dict[str, Any]]) -> float:
        if not ranked:
            return 0.0
        return round(sum(item["directional_confidence_pct"] for item in ranked[:3]) / min(3, len(ranked)), 1)


class PortfolioExecutionAgent:
    def allocate(self, request: dict[str, Any], consensus: dict[str, Any]) -> dict[str, Any]:
        capital = request["investor_profile"]["capital"]
        max_single = 0.25
        buys = [item for item in consensus["ranked_actions"] if item["action"] == "BUY"]
        holds = [item for item in consensus["ranked_actions"] if item["action"] == "HOLD"]
        sells = [item for item in consensus["ranked_actions"] if item["action"] == "SELL"]

        allocation: list[dict[str, Any]] = []
        if buys:
            total_buy_score = sum(max(0.01, item["directional_score"]) for item in buys)
            for item in buys:
                weight = clamp(max(0.01, item["directional_score"]) / total_buy_score * 0.70, 0.05, max_single)
                allocation.append(
                    {
                        "symbol": item["symbol"],
                        "action": "BUY",
                        "target_weight_pct": round(weight * 100, 1),
                        "target_value": round(capital * weight, 2),
                    }
                )
        for item in holds:
            allocation.append(
                {
                    "symbol": item["symbol"],
                    "action": "HOLD",
                    "target_weight_pct": 0.0,
                    "target_value": 0.0,
                }
            )
        for item in sells:
            allocation.append(
                {
                    "symbol": item["symbol"],
                    "action": "SELL_OR_REDUCE",
                    "target_weight_pct": 0.0,
                    "target_value": 0.0,
                }
            )

        invested_weight = sum(item["target_weight_pct"] for item in allocation if item["action"] == "BUY")
        cash_reserve_pct = round(max(0.0, 100.0 - invested_weight), 1)
        return {
            "allocation": allocation,
            "cash_reserve_pct": cash_reserve_pct,
            "execution_rules": [
                "Use limit orders and staged entries.",
                "Re-run committee if price moves more than 5% before execution.",
                "Do not exceed investor max drawdown and single-stock concentration constraints.",
            ],
        }


class ForensicLogger:
    def render(
        self,
        request: dict[str, Any],
        selected: list[AnalystAgent],
        evidence: list[Evidence],
        consensus: dict[str, Any],
        allocation: dict[str, Any],
    ) -> dict[str, Any]:
        critics = [
            item
            for item in evidence
            if item.source in {"RiskAssessment", "OpportunityCritic"} and item.action in {"SELL", "HOLD"}
        ]
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "decision_type": "investment_committee_research_plan",
            "investor_profile": request["investor_profile"],
            "agents_consulted": [
                {
                    "name": agent.profile.name,
                    "role": agent.profile.role,
                    "historical_reliability": agent.profile.historical_reliability,
                }
                for agent in selected
            ],
            "trade_output": consensus["ranked_actions"],
            "committee_confidence_pct": consensus["committee_confidence_pct"],
            "critic_comments": [
                {
                    "agent": item.source,
                    "symbol": item.symbol,
                    "action": item.action,
                    "confidence": round(item.confidence, 3),
                    "comment": item.rationale,
                    "metrics": item.metrics,
                }
                for item in critics[:8]
            ],
            "portfolio_plan": allocation,
            "forensic_log": [
                "Planner selected specialist agents based on investor risk tolerance, horizon, and available data.",
                "Each specialist produced symbol-level directional evidence with confidence.",
                "Consensus weighted evidence by agent reliability, directional confidence, and limited contrarian value.",
                "Portfolio execution converted consensus into capped target allocations and risk controls.",
            ],
            "not_financial_advice": "Research prototype only. Validate data, assumptions, taxes, suitability, and execution risk with a licensed professional.",
        }


def load_request(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the multi-agent investment planner.")
    parser.add_argument("--input", type=Path, default=Path("sample_request.json"), help="Path to request JSON.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()

    request = load_request(args.input)
    result = InvestmentPlannerAgent().run(request)
    if args.pretty:
        print(json.dumps(result, indent=2, sort_keys=False))
    else:
        print(json.dumps(result))


if __name__ == "__main__":
    main()
