"""Step-by-step replay of a single training or evaluation episode."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go

from rl.training_logger import EpisodeLog


class TrajectoryReplay:
    """Renders an episode's trajectory frame-by-frame for the Explainability Dashboard."""

    def __init__(self, grid: np.ndarray, episode_log: EpisodeLog) -> None:
        self.grid = grid
        self.episode_log = episode_log

    def total_frames(self) -> int:
        """Number of steps available to replay."""
        return len(self.episode_log.visited_states)

    def render_frame(self, step: int) -> np.ndarray:
        """Render a single frame as an RGB image, agent position at ``step``."""
        if not 0 <= step < self.total_frames():
            raise IndexError(f"Step {step} out of bounds for episode with {self.total_frames()} steps.")

        from vision.grid_extractor import _PREVIEW_CELL_SIZE_PX, _PREVIEW_COLORS

        cell_size = _PREVIEW_CELL_SIZE_PX
        rows, cols = self.grid.shape
        preview = np.tile(_PREVIEW_COLORS["free"], (rows * cell_size, cols * cell_size, 1))

        def paint(row: int, col: int, color: np.ndarray) -> None:
            r0, r1 = row * cell_size, (row + 1) * cell_size
            c0, c1 = col * cell_size, (col + 1) * cell_size
            preview[r0:r1, c0:c1] = color

        # Draw obstacles
        for r in range(rows):
            for c in range(cols):
                if self.grid[r, c] == 1:  # OBSTACLE
                    paint(r, c, _PREVIEW_COLORS["obstacle"])

        # Paint visited path up to step with trail color (sky blue)
        trail_color = np.array([186, 230, 253], dtype=np.uint8)  # sky-200
        for s in range(step + 1):
            st_idx = self.episode_log.visited_states[s]
            r, c = divmod(st_idx, cols)
            paint(r, c, trail_color)

        # Mark start cell if available
        if self.total_frames() > 0:
            start_r, start_c = divmod(self.episode_log.visited_states[0], cols)
            paint(start_r, start_c, _PREVIEW_COLORS["start"])

        # Mark current agent position
        agent_st = self.episode_log.visited_states[step]
        agent_r, agent_c = divmod(agent_st, cols)
        agent_color = np.array([59, 130, 246], dtype=np.uint8)  # blue-500
        paint(agent_r, agent_c, agent_color)

        return preview

    def render_animation(self) -> list[np.ndarray]:
        """Render every frame of the episode, for GIF/video export."""
        return [self.render_frame(s) for s in range(self.total_frames())]

    def render_plotly_frame(self, step: int) -> go.Figure:
        """Render an interactive Plotly figure for frame ``step``."""
        import plotly.graph_objects as go
        from rl.environment import OBSTACLE

        if not 0 <= step < self.total_frames():
            raise IndexError(f"Step {step} out of bounds for episode with {self.total_frames()} steps.")

        rows, cols = self.grid.shape
        fig = go.Figure()

        # Background grid matrix (1 for obstacle, 0 for free)
        bg_matrix = (self.grid == OBSTACLE).astype(float)

        fig.add_trace(
            go.Heatmap(
                z=bg_matrix,
                colorscale=[[0, "#1e293b"], [1, "#0f172a"]],  # dark background layout
                showscale=False,
                hoverinfo="none",
            )
        )

        # Path history
        path_states = self.episode_log.visited_states[: step + 1]
        path_coords = [divmod(st, cols) for st in path_states]
        path_rows = [p[0] for p in path_coords]
        path_cols = [p[1] for p in path_coords]

        fig.add_trace(
            go.Scatter(
                x=path_cols,
                y=path_rows,
                mode="lines+markers",
                line=dict(color="#38bdf8", width=3, dash="dot"),
                marker=dict(size=6, color="#38bdf8"),
                name="Path Trail",
                hoverinfo="text",
                hovertext=[f"Step {i}: ({r}, {c})" for i, (r, c) in enumerate(path_coords)],
            )
        )

        # Start position
        start_r, start_c = divmod(self.episode_log.visited_states[0], cols)
        fig.add_trace(
            go.Scatter(
                x=[start_c],
                y=[start_r],
                mode="markers",
                marker=dict(size=14, color="#10b981", symbol="square"),
                name="Start",
            )
        )

        # Current agent position
        curr_r, curr_c = path_coords[-1]
        fig.add_trace(
            go.Scatter(
                x=[curr_c],
                y=[curr_r],
                mode="markers+text",
                marker=dict(size=18, color="#f59e0b", symbol="circle"),
                text=["🤖"],
                textposition="middle center",
                name="Agent",
            )
        )

        fig.update_layout(
            title=dict(
                text=f"Trajectory Replay — Episode {self.episode_log.episode} (Step {step + 1} / {self.total_frames()})",
                x=0.5,
            ),
            xaxis=dict(range=[-0.5, cols - 0.5], dtick=1, title="Column"),
            yaxis=dict(range=[rows - 0.5, -0.5], dtick=1, title="Row"),  # inverted y for grid
            width=600,
            height=600,
            template="plotly_dark",
            margin=dict(l=40, r=40, t=60, b=40),
        )
        return fig

