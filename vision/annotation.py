"""Manual annotation of start/goal/obstacle/hazard cells over an extracted grid."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from rl.environment import GOAL, OBSTACLE, START


@dataclass
class AnnotationState:
    """User-provided annotations layered on top of the extracted occupancy grid."""

    # Starting (row, col) cell for the RL agent
    start_cell: tuple[int, int] | None = None
    # Goal (row, col) target cell for the mission
    goal_cell: tuple[int, int] | None = None
    # Set of manually added obstacle cells (impassable)
    obstacle_cells: set[tuple[int, int]] = field(default_factory=set)
    # Set of hazard cells (passable but heavily penalized)
    hazard_cells: set[tuple[int, int]] = field(default_factory=set)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-friendly dict (tuples -> lists)."""
        # Convert tuple coordinates and set data structures to standard JSON lists
        return {
            "start_cell": list(self.start_cell) if self.start_cell else None,
            "goal_cell": list(self.goal_cell) if self.goal_cell else None,
            "obstacle_cells": [list(cell) for cell in self.obstacle_cells],
            "hazard_cells": [list(cell) for cell in self.hazard_cells],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AnnotationState":
        """Rebuild an :class:`AnnotationState` from :meth:`to_dict` output."""
        # Reconstruct tuple coordinates and sets from JSON list format
        return cls(
            start_cell=tuple(data["start_cell"]) if data.get("start_cell") else None,
            goal_cell=tuple(data["goal_cell"]) if data.get("goal_cell") else None,
            obstacle_cells={tuple(cell) for cell in data.get("obstacle_cells", [])},
            hazard_cells={tuple(cell) for cell in data.get("hazard_cells", [])},
        )


class AnnotationManager:
    """Stateful helper the Manual Annotation page uses to edit an :class:`AnnotationState`."""

    def __init__(
        self,
        grid_shape: tuple[int, int],
        grid: np.ndarray | None = None,
        state: AnnotationState | None = None,
    ) -> None:
        self.grid_shape = grid_shape
        # Base occupancy grid array used for collision & conflict validation
        self.grid = grid
        self.state = state or AnnotationState()

    def _in_bounds(self, cell: tuple[int, int]) -> bool:
        """Helper to verify cell (row, col) lies within grid bounds."""
        row, col = cell
        return 0 <= row < self.grid_shape[0] and 0 <= col < self.grid_shape[1]

    def _is_base_obstacle(self, cell: tuple[int, int]) -> bool:
        """Whether ``cell`` is an obstacle in the underlying extracted grid."""
        if self.grid is None:
            return False
        return bool(self.grid[cell] == OBSTACLE)

    def set_start(self, cell: tuple[int, int]) -> None:
        """Set the agent's start cell."""
        if not self._in_bounds(cell):
            raise ValueError(f"Start cell {cell} is outside the {self.grid_shape} grid.")
        self.state.start_cell = cell

    def set_goal(self, cell: tuple[int, int]) -> None:
        """Set the mission goal cell."""
        if not self._in_bounds(cell):
            raise ValueError(f"Goal cell {cell} is outside the {self.grid_shape} grid.")
        self.state.goal_cell = cell

    def toggle_obstacle(self, cell: tuple[int, int]) -> None:
        """Add or remove a cell from the manually-marked obstacle set."""
        if not self._in_bounds(cell):
            raise ValueError(f"Cell {cell} is outside the {self.grid_shape} grid.")
        # Add if not present; remove if already in set
        if cell in self.state.obstacle_cells:
            self.state.obstacle_cells.remove(cell)
        else:
            self.state.obstacle_cells.add(cell)

    def toggle_hazard(self, cell: tuple[int, int]) -> None:
        """Add or remove a cell from the hazard set."""
        if not self._in_bounds(cell):
            raise ValueError(f"Cell {cell} is outside the {self.grid_shape} grid.")
        if cell in self.state.hazard_cells:
            self.state.hazard_cells.remove(cell)
        else:
            self.state.hazard_cells.add(cell)

    def validate(self) -> list[str]:
        """Return a list of human-readable validation errors, if any.

        A valid annotation requires a start cell, a goal cell, start !=
        goal, and neither cell on an obstacle (base grid or manual).
        """
        errors: list[str] = []
        state = self.state

        # Check required start and goal definitions
        if state.start_cell is None:
            errors.append("A start cell is required.")
        if state.goal_cell is None:
            errors.append("A goal cell is required.")
        if state.start_cell is not None and state.start_cell == state.goal_cell:
            errors.append("Start and goal cells must be different.")

        # Ensure start and goal are not positioned on base obstacles or manually placed obstacles
        for label, cell in (("Start", state.start_cell), ("Goal", state.goal_cell)):
            if cell is None:
                continue
            if self._is_base_obstacle(cell) or cell in state.obstacle_cells:
                errors.append(f"{label} cell {cell} cannot be on an obstacle.")

        return errors

    def build_annotated_grid(self) -> np.ndarray:
        """Overlay start/goal/obstacle annotations onto a copy of the base grid.

        Returns:
            A copy of the base grid with manual obstacles applied and
            ``START`` / ``GOAL`` cell codes set. Hazard cells are kept
            separately in ``self.state.hazard_cells`` for reward shaping
            (``rl.reward_presets``) rather than encoded as a grid value.

        Raises:
            ValueError: if this manager has no base grid to annotate.
        """
        if self.grid is None:
            raise ValueError("AnnotationManager has no base grid to annotate.")
        # Create non-mutating shallow copy of base occupancy grid
        annotated = self.grid.copy()
        # Mark manual obstacle cells
        for cell in self.state.obstacle_cells:
            annotated[cell] = OBSTACLE
        # Apply START and GOAL cell code values
        if self.state.start_cell is not None:
            annotated[self.state.start_cell] = START
        if self.state.goal_cell is not None:
            annotated[self.state.goal_cell] = GOAL
        return annotated
