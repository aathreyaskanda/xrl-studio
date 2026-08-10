"""Plotly line/bar charts summarizing training dynamics."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from rl.training_logger import TrainingLogger
from utils.constants import CHART_TYPES


def _empty_placeholder_figure(title: str) -> go.Figure:
    """A blank figure shown until the real chart logic is implemented."""
    figure = go.Figure()
    figure.update_layout(title=f"{title} (not yet implemented)")
    return figure


def plot_reward_vs_episode(logger: TrainingLogger, grid: np.ndarray) -> go.Figure:
    """Total reward per episode over training.

    TODO(visualization): implement. See PROJECT_PLAN.md, Phase 6.
    """
    return _empty_placeholder_figure("Reward vs Episode")


def plot_episode_length(logger: TrainingLogger, grid: np.ndarray) -> go.Figure:
    """Number of steps taken per episode over training.

    TODO(visualization): implement.
    """
    return _empty_placeholder_figure("Episode Length")


def plot_coverage_progress(logger: TrainingLogger, grid: np.ndarray) -> go.Figure:
    """Cumulative grid coverage fraction over training.

    TODO(visualization): implement, fed by ``analytics.coverage.coverage_over_time``.
    """
    return _empty_placeholder_figure("Coverage Progress")


def plot_exploration_rate(logger: TrainingLogger, grid: np.ndarray) -> go.Figure:
    """Epsilon decay curve over training.

    TODO(visualization): implement.
    """
    return _empty_placeholder_figure("Exploration Rate")


def plot_exploit_score(logger: TrainingLogger, grid: np.ndarray) -> go.Figure:
    """Reward-concentration ("exploit") score over training.

    TODO(visualization): implement, fed by ``analytics.reward_concentration``.
    """
    return _empty_placeholder_figure("Exploit Score")


def plot_state_visit_distribution(logger: TrainingLogger, grid: np.ndarray) -> go.Figure:
    """Histogram of how many times each state was visited.

    TODO(visualization): implement, fed by ``analytics.state_revisit``.
    """
    return _empty_placeholder_figure("State Visit Distribution")


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
