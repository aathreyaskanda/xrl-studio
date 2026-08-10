"""Plotly heatmaps: Coverage, Reward, Visit Frequency, Exploit, Loop Density."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from rl.training_logger import TrainingLogger
from utils.constants import HEATMAP_TYPES


def _empty_placeholder_figure(title: str) -> go.Figure:
    """A blank figure shown until the real heatmap logic is implemented."""
    figure = go.Figure()
    figure.update_layout(
        title=f"{title} (not yet implemented)",
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[{"text": "TODO", "showarrow": False, "font": {"size": 20}}],
    )
    return figure


def plot_coverage_heatmap(grid: np.ndarray, logger: TrainingLogger) -> go.Figure:
    """Heatmap of which cells were covered during training.

    TODO(visualization): implement, fed by ``analytics.state_revisit``.
    See PROJECT_PLAN.md, Phase 6.
    """
    return _empty_placeholder_figure("Coverage Heatmap")


def plot_reward_heatmap(grid: np.ndarray, logger: TrainingLogger) -> go.Figure:
    """Heatmap of cumulative reward earned per cell.

    TODO(visualization): implement.
    """
    return _empty_placeholder_figure("Reward Heatmap")


def plot_visit_frequency_heatmap(grid: np.ndarray, logger: TrainingLogger) -> go.Figure:
    """Heatmap of raw visit counts per cell, fed by ``analytics.state_revisit``.

    TODO(visualization): implement.
    """
    return _empty_placeholder_figure("Visit Frequency Heatmap")


def plot_exploit_heatmap(grid: np.ndarray, logger: TrainingLogger) -> go.Figure:
    """Heatmap highlighting cells associated with reward exploitation.

    TODO(visualization): implement, fed by ``analytics.reward_concentration``.
    """
    return _empty_placeholder_figure("Exploit Heatmap")


def plot_loop_density_heatmap(grid: np.ndarray, logger: TrainingLogger) -> go.Figure:
    """Heatmap of repeated-movement (loop) density per cell.

    TODO(visualization): implement, fed by ``analytics.loop_detection``.
    """
    return _empty_placeholder_figure("Loop Density Heatmap")


# Dispatch table used by the Explainability Dashboard page. Every renderer
# shares the signature (grid, logger) -> go.Figure for a uniform call site.
HEATMAP_RENDERERS = {
    "coverage": plot_coverage_heatmap,
    "reward": plot_reward_heatmap,
    "visit_frequency": plot_visit_frequency_heatmap,
    "exploit": plot_exploit_heatmap,
    "loop_density": plot_loop_density_heatmap,
}

assert set(HEATMAP_RENDERERS) == set(HEATMAP_TYPES), "Heatmap renderers must match HEATMAP_TYPES."
