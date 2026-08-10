"""Reward concentration analysis: is reward being earned broadly or exploited narrowly?"""

from __future__ import annotations

from rl.training_logger import TrainingLogger


def compute_reward_concentration(logger: TrainingLogger) -> dict[str, float]:
    """Summarize how concentrated reward collection is across states.

    A useful signal: a Gini-coefficient-style score over per-state reward
    totals. High concentration on a small state set is a reward-hacking
    indicator.

    Returns:
        A dict with at least a ``"gini_coefficient"`` key.

    TODO(analytics): implement.
    """
    raise NotImplementedError("compute_reward_concentration is not yet implemented.")
