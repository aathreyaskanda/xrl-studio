"""Plotly heatmaps: Coverage, Reward, Visit Frequency, Exploit, Loop Density."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from analytics.loop_detection import loop_density_grid
from analytics.state_revisit import compute_state_revisit_frequency
from rl.environment import OBSTACLE
from rl.training_logger import TrainingLogger
from utils.constants import HEATMAP_TYPES


def _create_heatmap_figure(
    matrix: np.ndarray,
    grid: np.ndarray,
    title: str,
    colorscale: str,
    colorbar_title: str,
    hover_label: str = "Value",
) -> go.Figure:
    """Helper to render a 2D matrix heatmap with grid overlay."""
    rows, cols = matrix.shape

    hover_text = [
        [
            f"Row {r}, Col {c}<br>{'Obstacle' if grid[r, c] == OBSTACLE else f'{hover_label}: {matrix[r, c]:.2f}'}"
            for c in range(cols)
        ]
        for r in range(rows)
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Heatmap(
            z=matrix,
            x=list(range(cols)),
            y=list(range(rows)),
            colorscale=colorscale,
            colorbar={"title": colorbar_title},
            text=hover_text,
            hoverinfo="text",
        )
    )

    obs_y, obs_x = np.where(grid == OBSTACLE)
    if len(obs_x) > 0:
        fig.add_trace(
            go.Scatter(
                x=obs_x,
                y=obs_y,
                mode="markers",
                marker={"symbol": "x", "color": "gray", "size": 8},
                name="Obstacle",
                hoverinfo="skip",
            )
        )

    fig.update_layout(
        title={"text": title, "x": 0.5, "xanchor": "center"},
        xaxis={"title": "Grid Column (x)", "dtick": max(1, cols // 10)},
        yaxis={"title": "Grid Row (y)", "autorange": "reversed", "dtick": max(1, rows // 10)},
        template="plotly_dark",
        margin={"l": 40, "r": 40, "t": 50, "b": 40},
    )

    return fig


def plot_coverage_heatmap(grid: np.ndarray, logger: TrainingLogger) -> go.Figure:
    """Heatmap of which cells were covered during training."""
    visit_counts = compute_state_revisit_frequency(logger, grid.shape)
    coverage_matrix = (visit_counts > 0).astype(float)
    return _create_heatmap_figure(
        coverage_matrix, grid, "Grid Coverage Heatmap", "Viridis", "Visited", "Coverage"
    )


def plot_reward_heatmap(grid: np.ndarray, logger: TrainingLogger) -> go.Figure:
    """Heatmap of cumulative reward earned per cell."""
    reward_matrix = np.zeros(grid.shape, dtype=float)
    cols = grid.shape[1]

    for ep in logger.get_logs():
        for state, r in zip(ep.visited_states, ep.rewards):
            row, col = divmod(state, cols)
            if 0 <= row < grid.shape[0] and 0 <= col < grid.shape[1]:
                reward_matrix[row, col] += r

    return _create_heatmap_figure(
        reward_matrix, grid, "Accumulated Reward Heatmap", "RdBu", "Reward", "Cumulative Reward"
    )


def plot_visit_frequency_heatmap(grid: np.ndarray, logger: TrainingLogger) -> go.Figure:
    """Heatmap of raw visit counts per cell."""
    visit_matrix = compute_state_revisit_frequency(logger, grid.shape).astype(float)
    return _create_heatmap_figure(
        visit_matrix, grid, "State Visit Frequency Heatmap", "Plasma", "Visits", "Visit Count"
    )


def plot_exploit_heatmap(grid: np.ndarray, logger: TrainingLogger) -> go.Figure:
    """Heatmap highlighting cells associated with reward exploitation."""
    exploit_matrix = np.zeros(grid.shape, dtype=float)
    cols = grid.shape[1]

    for ep in logger.get_logs():
        for state, r in zip(ep.visited_states, ep.rewards):
            if r > 0:
                row, col = divmod(state, cols)
                if 0 <= row < grid.shape[0] and 0 <= col < grid.shape[1]:
                    exploit_matrix[row, col] += r

    return _create_heatmap_figure(
        exploit_matrix, grid, "Reward Exploitation Heatmap", "Inferno", "Positive Reward", "Reward Exploited"
    )


def plot_loop_density_heatmap(grid: np.ndarray, logger: TrainingLogger) -> go.Figure:
    """Heatmap of repeated-movement (loop) density per cell."""
    loop_grid = loop_density_grid(logger.get_logs(), grid.shape)
    return _create_heatmap_figure(
        loop_grid, grid, "Loop Density Heatmap", "YlOrRd", "Loop Repeats", "Loop Density"
    )


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

