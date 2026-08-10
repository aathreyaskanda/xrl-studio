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
    """
    from rl.environment import OBSTACLE

    rows, cols = grid.shape
    q_table = agent.get_q_table()
    records = []

    for r in range(rows):
        for c in range(cols):
            state_idx = r * cols + c
            is_obstacle = grid[r, c] == OBSTACLE

            # Handle 2D vs 1D shapes for visit_counts and reward_per_cell
            if visit_counts.ndim == 2:
                v_count = int(visit_counts[r, c])
            else:
                v_count = int(visit_counts[state_idx])

            if reward_per_cell.ndim == 2:
                cell_reward = float(reward_per_cell[r, c])
            else:
                cell_reward = float(reward_per_cell[state_idx])

            if is_obstacle:
                records.append(
                    {
                        "Coordinates": f"({r}, {c})",
                        "Visit Count": v_count,
                        "Reward": cell_reward,
                        "Q-values": "N/A (Obstacle)",
                        "Best Action": "N/A",
                        "Policy Direction": "█",
                    }
                )
            else:
                if state_idx < len(q_table):
                    q_vals = q_table[state_idx]
                    best_act = int(np.argmax(q_vals))
                    q_str = f"U:{q_vals[0]:.2f}, D:{q_vals[1]:.2f}, L:{q_vals[2]:.2f}, R:{q_vals[3]:.2f}"
                    best_act_str = ACTIONS[best_act].capitalize()
                    arrow_str = action_to_arrow(best_act)
                else:
                    q_str = "N/A"
                    best_act_str = "Unknown"
                    arrow_str = "?"

                records.append(
                    {
                        "Coordinates": f"({r}, {c})",
                        "Visit Count": v_count,
                        "Reward": cell_reward,
                        "Q-values": q_str,
                        "Best Action": best_act_str,
                        "Policy Direction": arrow_str,
                    }
                )

    return pd.DataFrame(records, columns=POLICY_INSPECTOR_COLUMNS)



def action_to_arrow(action_index: int) -> str:
    """Map an action index to a directional arrow glyph for display."""
    arrows = {
        ACTIONS.index("up"): "↑",
        ACTIONS.index("down"): "↓",
        ACTIONS.index("left"): "←",
        ACTIONS.index("right"): "→",
    }
    return arrows.get(action_index, "?")
