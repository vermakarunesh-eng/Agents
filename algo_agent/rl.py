from __future__ import annotations

import random
from dataclasses import dataclass, field

from .data import PriceBar
from .features import FeatureRow, build_feature_rows
from .model import train_model


Action = str
State = tuple[str, str, str]
ACTIONS: tuple[Action, ...] = ("BUY", "SELL", "HOLD")


@dataclass(frozen=True)
class ReinforcementLearningConfig:
    horizon: int = 5
    train_window: int = 180
    episodes: int = 24
    learning_rate: float = 0.18
    discount: float = 0.88
    epsilon: float = 0.22
    epsilon_decay: float = 0.94
    min_epsilon: float = 0.03
    fee_bps: float = 3.0
    drawdown_penalty: float = 0.15


@dataclass(frozen=True)
class LearnedRule:
    state: State
    action: Action
    q_value: float

    def to_dict(self) -> dict[str, object]:
        return {
            "state": {
                "probability": self.state[0],
                "trend": self.state[1],
                "volatility": self.state[2],
            },
            "action": self.action,
            "q_value": round(self.q_value, 6),
        }


@dataclass(frozen=True)
class ReinforcementLearningResult:
    episodes: int
    start_date: str
    end_date: str
    total_return_pct: float
    buy_hold_return_pct: float
    max_drawdown_pct: float
    trades: int
    q_table: dict[State, dict[Action, float]] = field(repr=False)
    learned_rules: list[LearnedRule]

    def to_dict(self) -> dict[str, object]:
        return {
            "episodes": self.episodes,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "total_return_pct": self.total_return_pct,
            "buy_hold_return_pct": self.buy_hold_return_pct,
            "max_drawdown_pct": self.max_drawdown_pct,
            "trades": self.trades,
            "learned_rules": [rule.to_dict() for rule in self.learned_rules],
        }


def train_reinforcement_policy(
    bars: list[PriceBar],
    config: ReinforcementLearningConfig | None = None,
    seed: int = 7,
) -> ReinforcementLearningResult:
    config = config or ReinforcementLearningConfig()
    rows = build_feature_rows(bars, horizon=config.horizon)
    labeled = [row for row in rows if row.label is not None]
    if len(labeled) < config.train_window + config.horizon + 10:
        raise ValueError("Need more data for reinforcement learning. Try at least 320 daily bars.")

    states = _build_state_sequence(labeled, config.train_window)
    q_table = _initialize_q_table(states)
    rng = random.Random(seed)

    epsilon = config.epsilon
    for _ in range(config.episodes):
        _run_episode(labeled, states, q_table, config, epsilon, rng, learn=True)
        epsilon = max(config.min_epsilon, epsilon * config.epsilon_decay)

    equity, max_drawdown, trades = _run_episode(labeled, states, q_table, config, 0.0, rng, learn=False)
    first = labeled[config.train_window]
    last = labeled[-1]
    buy_hold = last.close / first.close - 1.0

    return ReinforcementLearningResult(
        episodes=config.episodes,
        start_date=first.date,
        end_date=last.date,
        total_return_pct=round((equity - 1.0) * 100.0, 2),
        buy_hold_return_pct=round(buy_hold * 100.0, 2),
        max_drawdown_pct=round(max_drawdown * 100.0, 2),
        trades=trades,
        q_table=q_table,
        learned_rules=_best_rules(q_table),
    )


def recommend_rl_action(probability: float, trend_score: float, volatility: float, q_table: dict[State, dict[Action, float]]) -> Action:
    state = _state_from_values(probability, trend_score, volatility)
    action_values = q_table.get(state)
    if not action_values:
        return "HOLD"
    return max(ACTIONS, key=lambda action: action_values[action])


def _build_state_sequence(rows: list[FeatureRow], train_window: int) -> list[State]:
    states: list[State] = []
    for index in range(train_window, len(rows)):
        train_slice = rows[index - train_window : index]
        model = train_model(
            [row.features for row in train_slice],
            [int(row.label) for row in train_slice],
            validation_fraction=0.2,
        )
        probability = model.predict_probability(rows[index].features)
        trend_score = rows[index].features[3] + rows[index].features[4]
        volatility = rows[index].features[5]
        states.append(_state_from_values(probability, trend_score, volatility))
    return states


def _state_from_values(probability: float, trend_score: float, volatility: float) -> State:
    if probability >= 0.58:
        probability_bucket = "prob_high"
    elif probability <= 0.42:
        probability_bucket = "prob_low"
    else:
        probability_bucket = "prob_mid"

    if trend_score > 0.02:
        trend_bucket = "trend_up"
    elif trend_score < -0.02:
        trend_bucket = "trend_down"
    else:
        trend_bucket = "trend_flat"

    if volatility >= 0.45:
        volatility_bucket = "vol_high"
    elif volatility <= 0.18:
        volatility_bucket = "vol_low"
    else:
        volatility_bucket = "vol_mid"

    return probability_bucket, trend_bucket, volatility_bucket


def _initialize_q_table(states: list[State]) -> dict[State, dict[Action, float]]:
    return {state: {action: 0.0 for action in ACTIONS} for state in set(states)}


def _run_episode(
    rows: list[FeatureRow],
    states: list[State],
    q_table: dict[State, dict[Action, float]],
    config: ReinforcementLearningConfig,
    epsilon: float,
    rng: random.Random,
    learn: bool,
) -> tuple[float, float, int]:
    equity = 1.0
    peak = 1.0
    max_drawdown = 0.0
    position = 0
    trades = 0
    fee = config.fee_bps / 10_000.0

    for offset in range(len(states) - 1):
        row_index = config.train_window + offset
        state = states[offset]
        action = _choose_action(q_table[state], epsilon, rng)
        desired_position = _position_for_action(action)

        if desired_position != position:
            equity *= 1.0 - fee
            trades += 1
            position = desired_position

        next_return = (rows[row_index + 1].close - rows[row_index].close) / rows[row_index].close
        step_return = position * next_return
        equity *= 1.0 + step_return
        peak = max(peak, equity)
        max_drawdown = min(max_drawdown, equity / peak - 1.0)
        reward = step_return - (abs(max_drawdown) * config.drawdown_penalty)

        if learn:
            next_state = states[offset + 1]
            current_q = q_table[state][action]
            best_next_q = max(q_table[next_state].values())
            q_table[state][action] = current_q + config.learning_rate * (
                reward + config.discount * best_next_q - current_q
            )

    return equity, max_drawdown, trades


def _choose_action(action_values: dict[Action, float], epsilon: float, rng: random.Random) -> Action:
    if rng.random() < epsilon:
        return rng.choice(ACTIONS)
    return max(ACTIONS, key=lambda action: action_values[action])


def _position_for_action(action: Action) -> int:
    if action == "BUY":
        return 1
    if action == "SELL":
        return -1
    return 0


def _best_rules(q_table: dict[State, dict[Action, float]]) -> list[LearnedRule]:
    rules = [
        LearnedRule(
            state=state,
            action=max(ACTIONS, key=lambda action: action_values[action]),
            q_value=max(action_values.values()),
        )
        for state, action_values in q_table.items()
    ]
    rules.sort(key=lambda rule: (rule.state[0], rule.state[1], rule.state[2]))
    return rules
