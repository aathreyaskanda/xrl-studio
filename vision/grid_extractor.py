"""OpenCV-based occupancy grid extraction from an uploaded layout image."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np

from rl.environment import OBSTACLE
from vision.annotation import AnnotationState

# Preview colors (RGB), keyed by what a cell represents.
_PREVIEW_COLORS = {
    "free": np.array([255, 255, 255], dtype=np.uint8),
    "obstacle": np.array([51, 65, 85], dtype=np.uint8),    # slate-700
    "start": np.array([16, 185, 129], dtype=np.uint8),     # emerald-500
    "goal": np.array([239, 68, 68], dtype=np.uint8),       # red-500
    "hazard": np.array([245, 158, 11], dtype=np.uint8),    # amber-500
}
_PREVIEW_CELL_SIZE_PX = 20


@dataclass
class GridExtractionConfig:
    """Parameters controlling how an image is converted into an occupancy grid."""

    grid_rows: int = 20
    grid_cols: int = 20
    binary_threshold: int = 127
    blur_kernel_size: int = 5
    invert: bool = False
    occupancy_vote_threshold: float = 0.5


class GridExtractor:
    """Converts a mission layout image into a discrete occupancy grid.

    Pipeline: grayscale -> Gaussian blur -> binary threshold -> cell-wise
    occupancy voting. By default, dark regions (e.g. walls drawn as dark
    lines on a light floor plan) are treated as obstacles; set
    ``invert=True`` for layouts where free space is the dark region.
    """

    def __init__(self, config: GridExtractionConfig | None = None) -> None:
        self.config = config or GridExtractionConfig()

    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """Grayscale, blur, and binarize the input image.

        Returns:
            A binary ``uint8`` array (values 0 or 255), same size as the
            input, where 255 marks "occupied" pixels.
        """
        config = self.config
        grayscale = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        kernel_size = max(1, config.blur_kernel_size)
        if kernel_size % 2 == 0:
            kernel_size += 1  # cv2.GaussianBlur requires an odd kernel size
        blurred = cv2.GaussianBlur(grayscale, (kernel_size, kernel_size), 0)

        # invert=False (default): dark pixels -> occupied (THRESH_BINARY_INV).
        # invert=True: light pixels -> occupied (THRESH_BINARY).
        threshold_type = cv2.THRESH_BINARY if config.invert else cv2.THRESH_BINARY_INV
        _, binary = cv2.threshold(blurred, config.binary_threshold, 255, threshold_type)
        return binary

    def extract_occupancy_grid(self, image: np.ndarray) -> np.ndarray:
        """Downsample a preprocessed binary image into an occupancy grid.

        Returns:
            An ``(grid_rows, grid_cols)`` int array using the cell codes
            defined in ``rl.environment`` (``FREE`` / ``OBSTACLE``).
        """
        config = self.config
        binary = self.preprocess(image)
        height, width = binary.shape

        grid = np.zeros((config.grid_rows, config.grid_cols), dtype=int)  # FREE == 0
        row_edges = np.linspace(0, height, config.grid_rows + 1, dtype=int)
        col_edges = np.linspace(0, width, config.grid_cols + 1, dtype=int)

        for row in range(config.grid_rows):
            for col in range(config.grid_cols):
                cell = binary[row_edges[row]:row_edges[row + 1], col_edges[col]:col_edges[col + 1]]
                if cell.size == 0:
                    continue
                occupied_fraction = float(np.count_nonzero(cell)) / cell.size
                if occupied_fraction >= config.occupancy_vote_threshold:
                    grid[row, col] = OBSTACLE

        return grid

    def visualize_grid(self, grid: np.ndarray, annotation: AnnotationState | None = None) -> np.ndarray:
        """Render the occupancy grid — optionally with annotations — as an RGB preview.

        Colors: white = free, slate = obstacle, emerald = start, red =
        goal, amber = hazard. Manually-added obstacle/hazard cells from
        ``annotation`` are painted even if absent from the base ``grid``.
        """
        cell_size = _PREVIEW_CELL_SIZE_PX
        rows, cols = grid.shape
        preview = np.tile(_PREVIEW_COLORS["free"], (rows * cell_size, cols * cell_size, 1))

        def paint(row: int, col: int, color: np.ndarray) -> None:
            r0, r1 = row * cell_size, (row + 1) * cell_size
            c0, c1 = col * cell_size, (col + 1) * cell_size
            preview[r0:r1, c0:c1] = color

        for row in range(rows):
            for col in range(cols):
                if grid[row, col] == OBSTACLE:
                    paint(row, col, _PREVIEW_COLORS["obstacle"])

        if annotation is not None:
            for cell in annotation.obstacle_cells:
                paint(*cell, _PREVIEW_COLORS["obstacle"])
            for cell in annotation.hazard_cells:
                paint(*cell, _PREVIEW_COLORS["hazard"])
            if annotation.start_cell is not None:
                paint(*annotation.start_cell, _PREVIEW_COLORS["start"])
            if annotation.goal_cell is not None:
                paint(*annotation.goal_cell, _PREVIEW_COLORS["goal"])

        return preview
