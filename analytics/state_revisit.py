"""State revisit-frequency analysis, backing the Visit Frequency heatmap."""

from __future__ import annotations

import numpy as np

from rl.training_logger import TrainingLogger


def compute_state_revisit_frequency(logger: TrainingLogger, grid_shape: tuple[int, int]) -> np.ndarray:
    """Count visits per cell across all episodes.

    Returns:
        An array of shape ``grid_shape`` with per-cell visit counts.

    TODO(analytics): implement.
    """
    raise NotImplementedError("compute_state_revisit_frequency is not yet implemented.")
