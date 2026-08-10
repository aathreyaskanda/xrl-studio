"""Detection of repetitive movement loops, a common reward-hacking symptom."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from rl.training_logger import EpisodeLog


@dataclass
class LoopEvent:
    """A detected cycle of revisited states within a single episode."""

    episode: int
    cycle_states: list[int]
    repeat_count: int


def detect_loops(episode_log: EpisodeLog, min_cycle_length: int = 2) -> list[LoopEvent]:
    """Find repeated state cycles within one episode's trajectory.

    TODO(analytics): implement, e.g. via a sliding-window repeat detector
    over ``episode_log.visited_states``.
    """
    raise NotImplementedError("detect_loops is not yet implemented.")


def loop_density_grid(episode_logs: list[EpisodeLog], grid_shape: tuple[int, int]) -> np.ndarray:
    """Aggregate loop activity per cell across episodes, for the Loop Density heatmap.

    TODO(analytics): implement.
    """
    raise NotImplementedError("loop_density_grid is not yet implemented.")
