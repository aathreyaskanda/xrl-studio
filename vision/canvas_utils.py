"""Pixel <-> grid-cell coordinate mapping for interactive editors."""

from __future__ import annotations


def pixel_to_cell(x: int, y: int, cell_size_px: int) -> tuple[int, int]:
    """Convert a click's pixel position on the preview image to (row, col)."""
    # Integer division maps canvas pixel offset (x, y) to discrete grid index (row, col)
    # y maps to row (vertical axis), x maps to col (horizontal axis)
    return y // cell_size_px, x // cell_size_px


def cell_to_pixel_bounds(row: int, col: int, cell_size_px: int) -> tuple[int, int, int, int]:
    """Return (x0, y0, x1, y1) pixel bounds for a given cell, for highlighting."""
    # Compute bounding rectangle pixel coordinates (left, top, right, bottom) for canvas drawing
    return col * cell_size_px, row * cell_size_px, (col + 1) * cell_size_px, (row + 1) * cell_size_px
