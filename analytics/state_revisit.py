"""State revisit-frequency analysis, backing the Visit Frequency heatmap."""

from __future__ import annotations

import numpy as np

from rl.training_logger import TrainingLogger


def compute_state_revisit_frequency(logger: TrainingLogger, grid_shape: tuple[int, int]) -> np.ndarray:
    """Count visits per cell across all episodes."""
    counts = np.zeros(grid_shape, dtype=int)
    n_cols = grid_shape[1]

    for ep in logger.get_logs():
        for state in ep.visited_states:
            row, col = divmod(state, n_cols)
            if 0 <= row < grid_shape[0] and 0 <= col < grid_shape[1]:
                counts[row, col] += 1

    return counts

