"""Reward concentration analysis: is reward being earned broadly or exploited narrowly?"""

from __future__ import annotations

from rl.training_logger import TrainingLogger

import numpy as np


def compute_reward_concentration(logger: TrainingLogger) -> dict[str, float]:
    """Summarize how concentrated reward collection is across states."""
    # Accumulate positive rewards earned per state index
    state_rewards: dict[int, float] = {}

    for ep in logger.get_logs():
        for state, reward in zip(ep.visited_states, ep.rewards):
            if reward > 0:
                state_rewards[state] = state_rewards.get(state, 0.0) + reward

    # Return zeroes if no positive rewards were earned across training
    if not state_rewards:
        return {
            "gini_coefficient": 0.0,
            "top_10pct_share": 0.0,
            "unique_states_rewarded": 0.0,
            "total_positive_reward": 0.0,
        }

    # Sort state reward values in ascending order
    rewards = np.sort(np.array(list(state_rewards.values()), dtype=float))
    n = len(rewards)
    total_reward = float(np.sum(rewards))

    if total_reward == 0.0 or n <= 1:
        gini = 0.0
        top_share = 1.0 if n == 1 else 0.0
    else:
        # Compute Gini Coefficient: measure of inequality in reward distribution (0 = equal, 1 = concentrated)
        indices = np.arange(1, n + 1)
        gini = float(np.sum((2 * indices - n - 1) * rewards) / (n * total_reward))

        # Compute share of total reward earned by top 10% most rewarded cells
        top_k = max(1, int(np.ceil(0.1 * n)))
        top_share = float(np.sum(rewards[-top_k:]) / total_reward)

    return {
        "gini_coefficient": round(float(gini), 4),
        "top_10pct_share": round(float(top_share), 4),
        "unique_states_rewarded": float(n),
        "total_positive_reward": round(total_reward, 2),
    }
