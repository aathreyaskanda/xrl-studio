"""Coverage analysis: how much of the navigable grid the agent actually visited."""

from __future__ import annotations

import numpy as np

from rl.training_logger import TrainingLogger


def compute_coverage(visited_states: set[int], total_navigable_states: int) -> float:
    """Fraction of navigable cells visited at least once, in ``[0, 1]``.

    TODO(analytics): implement.
    """
    raise NotImplementedError("compute_coverage is not yet implemented.")


def coverage_over_time(logger: TrainingLogger, total_navigable_states: int) -> np.ndarray:
    """Cumulative coverage fraction after each training episode.

    Returns:
        A 1D array of length ``n_episodes``, feeding
        ``visualization.charts.plot_coverage_progress``.

    TODO(analytics): implement.
    """
    raise NotImplementedError("coverage_over_time is not yet implemented.")
