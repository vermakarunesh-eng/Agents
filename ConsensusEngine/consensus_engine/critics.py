from __future__ import annotations

from consensus_engine.models import Critique, MarketContext


class Critic:
    critic_id: str

    def review(self, symbol: str, context: MarketContext) -> Critique | None:
        raise NotImplementedError


class RiskCritic(Critic):
    critic_id = "risk_critic"

    def review(self, symbol: str, context: MarketContext) -> Critique | None:
        data = context.candidates[symbol]
        drawdown = float(data.get("max_drawdown", 0.0))
        volatility = float(data.get("volatility", 0.0))
        severity = max(drawdown / 0.35, volatility / 0.45)
        if severity < 0.35:
            return None
        return Critique(
            self.critic_id,
            min(severity, 1.0),
            f"Risk profile requires sizing discipline: drawdown {drawdown:.1%}, volatility {volatility:.1%}.",
        )


class ProfitCritic(Critic):
    critic_id = "profit_critic"

    def review(self, symbol: str, context: MarketContext) -> Critique | None:
        data = context.candidates[symbol]
        expected_return = float(data.get("expected_return", 0.0))
        if expected_return >= 0.12:
            return None
        return Critique(
            self.critic_id,
            min(1.0, (0.12 - expected_return) / 0.12),
            f"Expected return {expected_return:.1%} is below the committee hurdle.",
        )


class MacroCritic(Critic):
    critic_id = "macro_critic"

    def review(self, symbol: str, context: MarketContext) -> Critique | None:
        data = context.candidates[symbol]
        policy = float(data.get("policy_tailwind", 0.0))
        if policy >= 0.05:
            return None
        return Critique(
            self.critic_id,
            min(1.0, abs(policy) + 0.25),
            f"Macro and policy alignment is weak for {data.get('name', symbol)}.",
        )


class OpportunityCritic(Critic):
    critic_id = "opportunity_critic"

    def review(self, symbol: str, context: MarketContext) -> Critique | None:
        current_return = float(context.candidates[symbol].get("expected_return", 0.0))
        better = [
            (candidate, float(data.get("expected_return", 0.0)))
            for candidate, data in context.candidates.items()
            if candidate != symbol
            and float(data.get("expected_return", 0.0)) > current_return + 0.04
        ]
        if not better:
            return None
        suggested_symbol, suggested_return = max(better, key=lambda item: item[1])
        return Critique(
            self.critic_id,
            min(1.0, suggested_return - current_return),
            (
                f"{context.candidates[suggested_symbol].get('name', suggested_symbol)} "
                f"offers stronger expected return at {suggested_return:.1%}."
            ),
            suggested_symbol=suggested_symbol,
        )


DEFAULT_CRITICS: tuple[Critic, ...] = (
    RiskCritic(),
    ProfitCritic(),
    MacroCritic(),
    OpportunityCritic(),
)
