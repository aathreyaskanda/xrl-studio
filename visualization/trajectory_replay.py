"""Step-by-step replay of a single training or evaluation episode."""

from __future__ import annotations

import numpy as np

from rl.training_logger import EpisodeLog


class TrajectoryReplay:
    """Renders an episode's trajectory frame-by-frame for the Explainability Dashboard.

    TODO(visualization): implement. See PROJECT_PLAN.md, Phase 7.
    """

    def __init__(self, grid: np.ndarray, episode_log: EpisodeLog) -> None:
        self.grid = grid
        self.episode_log = episode_log

    def total_frames(self) -> int:
        """Number of steps available to replay."""
        return len(self.episode_log.visited_states)

    def render_frame(self, step: int) -> np.ndarray:
        """Render a single frame as an RGB image, agent position at ``step``.

        TODO(visualization): implement, likely reusing
        ``visualization.heatmaps`` color conventions for consistency.
        """
        raise NotImplementedError("TrajectoryReplay.render_frame is not yet implemented.")

    def render_animation(self) -> list[np.ndarray]:
        """Render every frame of the episode, for GIF/video export.

        TODO(visualization): implement.
        """
        raise NotImplementedError("TrajectoryReplay.render_animation is not yet implemented.")
