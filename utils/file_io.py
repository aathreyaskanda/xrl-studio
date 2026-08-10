"""Filesystem helpers for saving and loading analysis-run artifacts."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np


def new_run_id() -> str:
    """Generate a unique, sortable identifier for an analysis run."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"{timestamp}-{uuid.uuid4().hex[:8]}"


def save_json(data: dict[str, Any], path: Path) -> Path:
    """Write a dict to disk as pretty-printed JSON, creating parents as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=2, default=str)
    return path


def load_json(path: Path) -> dict[str, Any]:
    """Read a JSON file back into a dict."""
    with open(path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)


def save_grid_csv(grid: np.ndarray, path: Path) -> Path:
    """Persist an occupancy grid as CSV, for export/debugging."""
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savetxt(path, grid, delimiter=",", fmt="%d")
    return path


def load_grid_csv(path: Path) -> np.ndarray:
    """Load an occupancy grid previously saved with :func:`save_grid_csv`."""
    return np.loadtxt(path, delimiter=",", dtype=int)
