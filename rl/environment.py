"""Gymnasium-compatible GridWorld environment used for every mission profile.

The environment is mission-agnostic: mission profiles only change labels
and the :class:`~rl.reward_presets.RewardConfig` passed in, never the
environment mechanics. See PROJECT_PLAN.md, Phase 3.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from rl.reward_presets import RewardConfig

# Cell values used in the occupancy grid produced by vision.grid_extractor.
# 0 = free cell, 1 = obstacle cell, 2 = goal cell, 3 = start cell.
FREE = 0
OBSTACLE = 1
GOAL = 2
START = 3


@dataclass
class EnvironmentConfig:
    """Everything needed to construct a :class:`GridWorldEnv`."""

    # 2D occupancy grid array (0=free, 1=obstacle)
    grid: np.ndarray
    # Starting (row, col) coordinates of the agent
    start_pos: tuple[int, int]
    # Destination (row, col) target coordinates
    goal_pos: tuple[int, int]
    # Reward shaping weights (step penalty, goal reward, revisit penalty, etc.)
    reward_config: RewardConfig
    # Maximum steps per episode before truncation occurs
    max_steps: int = 200
    # Optional set of hazard cells for extra hazard penalties
    hazard_cells: set[tuple[int, int]] = field(default_factory=set)


class GridWorldEnv(gym.Env):
    """A discrete grid-world navigation environment.

    Observation: the agent's ``(row, col)`` position, encoded as a single
    integer state index (``row * n_cols + col``) for tabular Q-learning.
    Action space: 4 discrete moves — see ``utils.constants.ACTIONS`` for
    the up/down/left/right index convention.
    """

    metadata = {"render_modes": ["rgb_array"]}

    def __init__(self, config: EnvironmentConfig) -> None:
        super().__init__()
        self.config = config
        self.n_rows, self.n_cols = config.grid.shape
        # Action space: 4 discrete directional moves (0: Up, 1: Down, 2: Left, 3: Right)
        self.action_space = spaces.Discrete(4)
        # Observation space: 1D discrete state index space (n_rows * n_cols)
        self.observation_space = spaces.Discrete(self.n_rows * self.n_cols)
        # Initialize internal agent position tracker to starting coordinates
        self.agent_pos: tuple[int, int] = config.start_pos
        self._elapsed_steps = 0
        # Track unique cell visits within the current episode for coverage bonuses and revisit penalties
        self._visited_in_episode: set[tuple[int, int]] = set()

    def pos_to_state(self, pos: tuple[int, int]) -> int:
        """Encode a ``(row, col)`` position as a single state index."""
        # Tabular Q-learning needs one integer per distinct state (see
        # rl/q_learning.py's q_table, shaped (n_states, n_actions)). We use
        # row-major ("C order") encoding — the same layout NumPy uses by
        # default — so state index and (row, col) always convert back and
        # forth consistently via this method and state_to_pos() below.
        row, col = pos
        return row * self.n_cols + col

    def state_to_pos(self, state: int) -> tuple[int, int]:
        """Decode a state index back into a ``(row, col)`` position."""
        # Inverse row-major mapping using integer division and modulo
        return divmod(state, self.n_cols)

    def reset(self, *, seed: int | None = None, options: dict | None = None) -> tuple[int, dict]:
        """Reset the agent to the configured start position."""
        # Reset Gymnasium environment random seed if provided
        super().reset(seed=seed)
        # Restore starting position, step count, and visited state set
        self.agent_pos = self.config.start_pos
        self._elapsed_steps = 0
        self._visited_in_episode = {self.agent_pos}
        # Encode position tuple to 1D integer state observation
        obs = self.pos_to_state(self.agent_pos)
        info = {"agent_pos": self.agent_pos}
        return obs, info

    def step(self, action: int) -> tuple[int, float, bool, bool, dict]:
        """Apply an action and return ``(obs, reward, terminated, truncated, info)``."""
        # Map discrete action index (0..3) to coordinate deltas (dr, dc)
        dr, dc = 0, 0
        if action == 0:  # up
            dr, dc = -1, 0
        elif action == 1:  # down
            dr, dc = 1, 0
        elif action == 2:  # left
            dr, dc = 0, -1
        elif action == 3:  # right
            dr, dc = 0, 1

        # Compute target candidate position
        next_row = self.agent_pos[0] + dr
        next_col = self.agent_pos[1] + dc

        # Check bounds and obstacle collision criteria
        collided = False
        if not (0 <= next_row < self.n_rows and 0 <= next_col < self.n_cols):
            collided = True
        elif self.config.grid[next_row, next_col] == OBSTACLE:
            collided = True

        # Base step reward penalty to encourage efficient pathing
        cfg = self.config.reward_config
        reward = cfg.step_penalty

        # Apply collision penalty if moving out of bounds or into an obstacle cell
        if collided:
            reward += cfg.collision_penalty
        else:
            # Advance agent position if move is valid
            self.agent_pos = (next_row, next_col)

        # Check goal termination condition
        terminated = False
        if self.agent_pos == self.config.goal_pos:
            reward += cfg.goal_reward
            terminated = True
        else:
            # Reward shaping: penalty for revisiting already-explored cells, bonus for new cells
            if self.agent_pos in self._visited_in_episode:
                reward += cfg.revisit_penalty
            else:
                reward += cfg.coverage_bonus
                self._visited_in_episode.add(self.agent_pos)

        # Apply additional hazard penalty if agent steps into a hazard cell
        if self.agent_pos in self.config.hazard_cells:
            reward += cfg.hazard_penalty

        # Increment step counter and check maximum step truncation condition
        self._elapsed_steps += 1
        truncated = self._elapsed_steps >= self.config.max_steps

        obs = self.pos_to_state(self.agent_pos)
        info = {
            "agent_pos": self.agent_pos,
            "collided": collided,
            "reached_goal": terminated,
            "steps": self._elapsed_steps,
        }
        return obs, reward, terminated, truncated, info

    def render(self) -> np.ndarray:
        """Return an RGB array representation of the current grid state."""
        from vision.annotation import AnnotationState
        from vision.grid_extractor import GridExtractor

        # Package current runtime grid state into AnnotationState overlay for preview rendering
        annotation = AnnotationState(
            start_cell=self.agent_pos,
            goal_cell=self.config.goal_pos,
            hazard_cells=set(self.config.hazard_cells),
        )
        return GridExtractor().visualize_grid(self.config.grid, annotation)
