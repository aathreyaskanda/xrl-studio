"""Coverage analysis: how much of the navigable grid the agent actually visited."""

from __future__ import annotations

import numpy as np

from rl.training_logger import TrainingLogger


def compute_coverage(visited_states: set[int], total_navigable_states: int) -> float:
    """Fraction of navigable cells visited at least once, in ``[0, 1]``."""
    if total_navigable_states <= 0:
        return 0.0
    return float(min(1.0, len(visited_states) / total_navigable_states))


def coverage_over_time(logger: TrainingLogger, total_navigable_states: int) -> np.ndarray:
    """Cumulative coverage fraction after each training episode.

    Returns:
        A 1D array of length ``n_episodes``, feeding
        ``visualization.charts.plot_coverage_progress``.
    """
    episodes = logger.get_logs()
    if not episodes:
        return np.array([], dtype=float)

    visited_so_far: set[int] = set()
    coverage_series = np.zeros(len(episodes), dtype=float)

    for i, ep in enumerate(episodes):
        visited_so_far.update(ep.visited_states)
        coverage_series[i] = compute_coverage(visited_so_far, total_navigable_states)

    return coverage_series

