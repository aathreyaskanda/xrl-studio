"""Plotly line/bar charts summarizing training dynamics."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from analytics.coverage import coverage_over_time
from analytics.state_revisit import compute_state_revisit_frequency
from rl.environment import OBSTACLE
from rl.training_logger import TrainingLogger
from utils.constants import CHART_TYPES


def plot_reward_vs_episode(logger: TrainingLogger, grid: np.ndarray) -> go.Figure:
    """Total reward per episode over training."""
    episodes = [ep.episode for ep in logger.get_logs()]
    rewards = [ep.total_reward for ep in logger.get_logs()]

    rolling = pd.Series(rewards).rolling(10, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=episodes,
            y=rewards,
            mode="lines",
            name="Total Reward",
            line={"color": "rgba(99, 110, 250, 0.4)", "width": 1},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=episodes,
            y=rolling,
            mode="lines",
            name="10-Ep Rolling Avg",
            line={"color": "#636EFA", "width": 2.5},
        )
    )

    fig.update_layout(
        title={"text": "Total Reward vs Episode", "x": 0.5, "xanchor": "center"},
        xaxis={"title": "Episode"},
        yaxis={"title": "Total Reward"},
        template="plotly_dark",
        margin={"l": 40, "r": 40, "t": 50, "b": 40},
    )
    return fig


def plot_episode_length(logger: TrainingLogger, grid: np.ndarray) -> go.Figure:
    """Number of steps taken per episode over training."""
    episodes = [ep.episode for ep in logger.get_logs()]
    steps = [ep.steps for ep in logger.get_logs()]

    rolling = pd.Series(steps).rolling(10, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=episodes,
            y=steps,
            mode="lines",
            name="Steps",
            line={"color": "rgba(239, 85, 59, 0.4)", "width": 1},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=episodes,
            y=rolling,
            mode="lines",
            name="10-Ep Rolling Avg",
            line={"color": "#EF553B", "width": 2.5},
        )
    )

    fig.update_layout(
        title={"text": "Episode Length (Steps per Episode)", "x": 0.5, "xanchor": "center"},
        xaxis={"title": "Episode"},
        yaxis={"title": "Steps"},
        template="plotly_dark",
        margin={"l": 40, "r": 40, "t": 50, "b": 40},
    )
    return fig


def plot_coverage_progress(logger: TrainingLogger, grid: np.ndarray) -> go.Figure:
    """Cumulative grid coverage fraction over training."""
    episodes = [ep.episode for ep in logger.get_logs()]
    navigable_count = int(np.count_nonzero(grid != OBSTACLE)) if grid is not None else 100
    cov_series = coverage_over_time(logger, navigable_count) * 100.0

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=episodes,
            y=cov_series,
            mode="lines",
            name="Cumulative Coverage",
            line={"color": "#00CC96", "width": 2.5},
        )
    )

    fig.update_layout(
        title={"text": "Cumulative Grid Coverage over Training", "x": 0.5, "xanchor": "center"},
        xaxis={"title": "Episode"},
        yaxis={"title": "Coverage (%)", "range": [0, 105]},
        template="plotly_dark",
        margin={"l": 40, "r": 40, "t": 50, "b": 40},
    )
    return fig


def plot_exploration_rate(logger: TrainingLogger, grid: np.ndarray) -> go.Figure:
    """Epsilon decay curve over training."""
    episodes = [ep.episode for ep in logger.get_logs()]
    epsilons = [ep.epsilon for ep in logger.get_logs()]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=episodes,
            y=epsilons,
            mode="lines",
            name="Epsilon (Exploration)",
            line={"color": "#AB63FA", "width": 2.5},
        )
    )

    fig.update_layout(
        title={"text": "Exploration Rate (Epsilon Decay)", "x": 0.5, "xanchor": "center"},
        xaxis={"title": "Episode"},
        yaxis={"title": "Epsilon", "range": [0, 1.05]},
        template="plotly_dark",
        margin={"l": 40, "r": 40, "t": 50, "b": 40},
    )
    return fig


def plot_exploit_score(logger: TrainingLogger, grid: np.ndarray) -> go.Figure:
    """Reward-concentration ("exploit") score over training."""
    episodes = [ep.episode for ep in logger.get_logs()]
    pos_rewards = [sum(r for r in ep.rewards if r > 0) for ep in logger.get_logs()]
    rolling = pd.Series(pos_rewards).rolling(10, min_periods=1).mean()

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=episodes,
            y=pos_rewards,
            name="Positive Reward",
            marker={"color": "rgba(255, 161, 84, 0.4)"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=episodes,
            y=rolling,
            mode="lines",
            name="10-Ep Rolling Avg",
            line={"color": "#FFA154", "width": 2.5},
        )
    )

    fig.update_layout(
        title={"text": "Positive Reward Exploitation per Episode", "x": 0.5, "xanchor": "center"},
        xaxis={"title": "Episode"},
        yaxis={"title": "Positive Reward Earned"},
        template="plotly_dark",
        margin={"l": 40, "r": 40, "t": 50, "b": 40},
    )
    return fig


def plot_state_visit_distribution(logger: TrainingLogger, grid: np.ndarray) -> go.Figure:
    """Histogram of how many times each state was visited."""
    visit_matrix = compute_state_revisit_frequency(logger, grid.shape)
    free_mask = (grid != OBSTACLE)
    counts = visit_matrix[free_mask].flatten()

    fig = go.Figure()
    fig.add_trace(
        go.Histogram(
            x=counts,
            nbinsx=30,
            marker={"color": "#19D3F3"},
            name="Cell Visits",
        )
    )

    fig.update_layout(
        title={"text": "State Visit Frequency Distribution", "x": 0.5, "xanchor": "center"},
        xaxis={"title": "Visits per Cell"},
        yaxis={"title": "Number of Free Cells"},
        template="plotly_dark",
        margin={"l": 40, "r": 40, "t": 50, "b": 40},
    )
    return fig


# Dispatch table used by the Explainability Dashboard page. Every renderer
# shares the signature (logger, grid) -> go.Figure for a uniform call site.
CHART_RENDERERS = {
    "reward_vs_episode": plot_reward_vs_episode,
    "episode_length": plot_episode_length,
    "coverage_progress": plot_coverage_progress,
    "exploration_rate": plot_exploration_rate,
    "exploit_score": plot_exploit_score,
    "state_visit_distribution": plot_state_visit_distribution,
}

assert set(CHART_RENDERERS) == set(CHART_TYPES), "Chart renderers must match CHART_TYPES."

