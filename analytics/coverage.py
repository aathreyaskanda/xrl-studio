"""Coverage analysis: how much of the navigable grid the agent actually visited."""

from __future__ import annotations

import numpy as np

from rl.training_logger import TrainingLogger


def compute_coverage(visited_states: set[int], total_navigable_states: int) -> float:
    """Fraction of navigable cells visited at least once, in ``[0, 1]``."""
    # Guard against division by zero if total navigable state count is invalid
    if total_navigable_states <= 0:
        return 0.0
    # Compute ratio of unique visited state count to total navigable cells, capped at 1.0
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

    # Accumulator set tracking unique state indices visited across training progression
    visited_so_far: set[int] = set()
    # Output array storing cumulative coverage percentage for each episode
    coverage_series = np.zeros(len(episodes), dtype=float)

    for i, ep in enumerate(episodes):
        # Union visited states from current episode into historical accumulator
        visited_so_far.update(ep.visited_states)
        # Calculate running coverage fraction
        coverage_series[i] = compute_coverage(visited_so_far, total_navigable_states)

    return coverage_series
