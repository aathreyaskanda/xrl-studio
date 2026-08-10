"""Tabular inspection of the learned policy, cell by cell."""

from __future__ import annotations

import numpy as np
import pandas as pd

from rl.q_learning import QLearningAgent
from utils.constants import ACTIONS

POLICY_INSPECTOR_COLUMNS = [
    "Coordinates",
    "Visit Count",
    "Reward",
    "Q-values",
    "Best Action",
    "Policy Direction",
]


def build_policy_table(
    agent: QLearningAgent,
    grid: np.ndarray,
    visit_counts: np.ndarray,
    reward_per_cell: np.ndarray,
) -> pd.DataFrame:
    """Assemble the Policy Inspector table shown on the Explainability Dashboard.

    Returns:
        A DataFrame with columns ``POLICY_INSPECTOR_COLUMNS``, one row per grid cell.

    TODO(visualization): implement. See PROJECT_PLAN.md, Phase 7.
    """
    raise NotImplementedError("build_policy_table is not yet implemented.")


def action_to_arrow(action_index: int) -> str:
    """Map an action index to a directional arrow glyph for display."""
    arrows = {
        ACTIONS.index("up"): "↑",
        ACTIONS.index("down"): "↓",
        ACTIONS.index("left"): "←",
        ACTIONS.index("right"): "→",
    }
    return arrows.get(action_index, "?")
