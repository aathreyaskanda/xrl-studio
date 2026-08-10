"""A library of ready-made benchmark layouts for quick demos and learning."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class BenchmarkLayout:
    """A pre-built grid layout associated with a mission profile."""

    name: str
    mission_key: str
    description: str
    grid_shape: tuple[int, int] = (20, 20)
    start_cell: tuple[int, int] = (0, 0)
    goal_cell: tuple[int, int] = (19, 19)
    obstacle_cells: set[tuple[int, int]] = field(default_factory=set)
    hazard_cells: set[tuple[int, int]] = field(default_factory=set)
    grid: np.ndarray | None = None  # populated lazily by build_grid()
    thumbnail_path: str | None = None

    def build_grid(self) -> np.ndarray:
        """Construct this benchmark's occupancy grid on demand."""
        if self.grid is not None:
            return self.grid
        rows, cols = self.grid_shape
        grid = np.zeros((rows, cols), dtype=int)
        for r, c in self.obstacle_cells:
            if 0 <= r < rows and 0 <= c < cols:
                grid[r, c] = OBSTACLE
        self.grid = grid
        return self.grid

    def build_annotation(self) -> AnnotationState:
        """Construct the matching AnnotationState for this benchmark."""
        from vision.annotation import AnnotationState

        return AnnotationState(
            start_cell=self.start_cell,
            goal_cell=self.goal_cell,
            obstacle_cells=set(),
            hazard_cells=set(self.hazard_cells),
        )


def _build_warehouse_benchmarks() -> list[BenchmarkLayout]:
    # Layout 1: Standard Aisles (20x20)
    obs_1: set[tuple[int, int]] = set()
    for col in (3, 4, 7, 8, 11, 12, 15, 16):
        for row in range(2, 18):
            if row not in (9, 10):  # Cross aisle
                obs_1.add((row, col))
    haz_1 = {(5, 2), (14, 10), (5, 9), (14, 17)}

    # Layout 2: Central Hub (15x15)
    obs_2: set[tuple[int, int]] = set()
    for r in range(3, 12):
        for c in range(3, 12):
            if r != 7 and c != 7:
                obs_2.add((r, c))
    haz_2 = {(2, 7), (12, 5), (7, 2), (7, 12)}

    return [
        BenchmarkLayout(
            name="Standard Aisles",
            mission_key="warehouse_inspection",
            description="20x20 grid with vertical shelving rows, cross aisles, and spill hazard zones.",
            grid_shape=(20, 20),
            start_cell=(1, 1),
            goal_cell=(18, 18),
            obstacle_cells=obs_1,
            hazard_cells=haz_1,
        ),
        BenchmarkLayout(
            name="Central Storage Hub",
            mission_key="warehouse_inspection",
            description="15x15 grid with a central storage block and perimeter/cross aisles.",
            grid_shape=(15, 15),
            start_cell=(0, 0),
            goal_cell=(14, 14),
            obstacle_cells=obs_2,
            hazard_cells=haz_2,
        ),
    ]


def _build_hospital_benchmarks() -> list[BenchmarkLayout]:
    # Layout 1: Ward Floor Plan (20x20)
    obs_1: set[tuple[int, int]] = set()
    # Horizontal corridor walls
    for c in range(20):
        if c != 10:
            obs_1.add((6, c))
            obs_1.add((13, c))
    # Vertical ward partition walls
    for r in range(0, 6):
        if r != 3:
            obs_1.add((r, 5))
            obs_1.add((r, 15))
    for r in range(14, 20):
        if r != 17:
            obs_1.add((r, 5))
            obs_1.add((r, 15))
    haz_1 = {(8, 2), (8, 3), (15, 14), (2, 8)}

    # Layout 2: Emergency Department (15x15)
    obs_2: set[tuple[int, int]] = set()
    for c in range(15):
        if c != 7:
            obs_2.add((4, c))
            obs_2.add((10, c))
    for r in range(0, 4):
        if r != 2:
            obs_2.add((r, 4))
    for r in range(10, 15):
        if r != 12:
            obs_2.add((r, 10))
    haz_2 = {(2, 2), (12, 12), (7, 2)}

    return [
        BenchmarkLayout(
            name="Ward Floor Plan",
            mission_key="hospital_delivery",
            description="20x20 grid featuring patient ward rooms, main corridors, and restricted ICU hazards.",
            grid_shape=(20, 20),
            start_cell=(1, 1),
            goal_cell=(18, 18),
            obstacle_cells=obs_1,
            hazard_cells=haz_1,
        ),
        BenchmarkLayout(
            name="Emergency Department",
            mission_key="hospital_delivery",
            description="15x15 grid layout of an ER department with triage bays and restricted zones.",
            grid_shape=(15, 15),
            start_cell=(0, 7),
            goal_cell=(14, 7),
            obstacle_cells=obs_2,
            hazard_cells=haz_2,
        ),
    ]


def _build_security_benchmarks() -> list[BenchmarkLayout]:
    # Layout 1: Office Cubicle Floor (20x20)
    obs_1: set[tuple[int, int]] = set()
    cubicle_top_lefts = [
        (3, 3), (3, 8), (3, 13),
        (8, 3), (8, 13),
        (13, 3), (13, 8), (13, 13),
    ]
    for tr, tc in cubicle_top_lefts:
        for dr in (0, 1):
            for dc in (0, 1):
                obs_1.add((tr + dr, tc + dc))
    haz_1 = {(5, 5), (5, 15), (15, 5), (15, 15), (10, 8)}

    # Layout 2: Perimeter Gallery (15x15)
    obs_2: set[tuple[int, int]] = set()
    for r in range(3, 12):
        for c in range(3, 12):
            if not (r == 7 and c == 7):
                obs_2.add((r, c))
    haz_2 = {(1, 13), (13, 1), (7, 1)}

    return [
        BenchmarkLayout(
            name="Office Cubicle Floor",
            mission_key="indoor_security_patrol",
            description="20x20 office layout with cubicle blocks, open hallways, and camera blind spot hazards.",
            grid_shape=(20, 20),
            start_cell=(1, 1),
            goal_cell=(18, 18),
            obstacle_cells=obs_1,
            hazard_cells=haz_1,
        ),
        BenchmarkLayout(
            name="Perimeter Gallery",
            mission_key="indoor_security_patrol",
            description="15x15 gallery layout with a central exhibit hall and outer patrol corridor.",
            grid_shape=(15, 15),
            start_cell=(1, 1),
            goal_cell=(13, 13),
            obstacle_cells=obs_2,
            hazard_cells=haz_2,
        ),
    ]


def _build_industrial_benchmarks() -> list[BenchmarkLayout]:
    # Layout 1: Refinery Plant (20x20)
    obs_1: set[tuple[int, int]] = set()
    machine_blocks = [
        (3, 3, 4, 5), (13, 3, 4, 5),
        (3, 12, 4, 5), (13, 12, 4, 5),
    ]
    for r0, c0, dr, dc in machine_blocks:
        for r in range(r0, r0 + dr):
            for c in range(c0, c0 + dc):
                obs_1.add((r, c))
    haz_1 = {(2, 5), (7, 5), (12, 5), (17, 5), (5, 11), (14, 11)}

    # Layout 2: Assembly Conveyors (15x15)
    obs_2: set[tuple[int, int]] = set()
    for c in range(1, 14):
        if c != 7:
            obs_2.add((3, c))
            obs_2.add((11, c))
    haz_2 = {(2, 7), (12, 7), (7, 3), (7, 11)}

    return [
        BenchmarkLayout(
            name="Refinery Plant",
            mission_key="industrial_facility_inspection",
            description="20x20 industrial layout with heavy machinery blocks and hot steam hazard zones.",
            grid_shape=(20, 20),
            start_cell=(0, 0),
            goal_cell=(19, 19),
            obstacle_cells=obs_1,
            hazard_cells=haz_1,
        ),
        BenchmarkLayout(
            name="Assembly Conveyors",
            mission_key="industrial_facility_inspection",
            description="15x15 plant layout with dual assembly line conveyors and high-voltage hazards.",
            grid_shape=(15, 15),
            start_cell=(0, 0),
            goal_cell=(14, 14),
            obstacle_cells=obs_2,
            hazard_cells=haz_2,
        ),
    ]


def _build_rescue_benchmarks() -> list[BenchmarkLayout]:
    # Layout 1: Collapsed Building (20x20)
    obs_1: set[tuple[int, int]] = {
        (3, 3), (3, 4), (4, 3), (8, 7), (8, 8), (9, 8),
        (12, 14), (13, 14), (14, 14), (16, 2), (16, 3),
        (5, 12), (6, 12), (7, 12), (11, 4), (12, 4),
        (2, 15), (3, 15), (15, 9), (15, 10),
    }
    haz_1 = {(5, 5), (10, 12), (14, 6), (7, 16)}

    # Layout 2: Flooded Sub-level (15x15)
    obs_2: set[tuple[int, int]] = set()
    for c in range(0, 11):
        if c != 5:
            obs_2.add((5, c))
    for c in range(4, 15):
        if c != 9:
            obs_2.add((9, c))
    haz_2 = {(3, 5), (4, 5), (11, 9), (12, 9), (7, 7)}

    return [
        BenchmarkLayout(
            name="Collapsed Building",
            mission_key="search_rescue",
            description="20x20 disaster area with debris obstacle clusters and unstable structure hazards.",
            grid_shape=(20, 20),
            start_cell=(1, 1),
            goal_cell=(18, 18),
            obstacle_cells=obs_1,
            hazard_cells=haz_1,
        ),
        BenchmarkLayout(
            name="Flooded Sub-level",
            mission_key="search_rescue",
            description="15x15 subterranean layout with structural breaches and deep water hazard zones.",
            grid_shape=(15, 15),
            start_cell=(0, 0),
            goal_cell=(14, 14),
            obstacle_cells=obs_2,
            hazard_cells=haz_2,
        ),
    ]


# Registered benchmark layouts, keyed by mission.
BENCHMARK_LIBRARY: dict[str, list[BenchmarkLayout]] = {
    "warehouse_inspection": _build_warehouse_benchmarks(),
    "hospital_delivery": _build_hospital_benchmarks(),
    "indoor_security_patrol": _build_security_benchmarks(),
    "industrial_facility_inspection": _build_industrial_benchmarks(),
    "search_rescue": _build_rescue_benchmarks(),
}


def list_benchmarks(mission_key: str | None = None) -> list[BenchmarkLayout]:
    """List benchmark layouts, optionally filtered to a single mission."""
    if mission_key is not None:
        return BENCHMARK_LIBRARY.get(mission_key, [])
    return [layout for layouts in BENCHMARK_LIBRARY.values() for layout in layouts]


def get_benchmark(mission_key: str, name: str) -> BenchmarkLayout:
    """Look up a single benchmark layout by mission and name.

    Raises:
        KeyError: if no matching layout is registered.
    """
    for layout in BENCHMARK_LIBRARY.get(mission_key, []):
        if layout.name == name:
            return layout
    raise KeyError(f"No benchmark named {name!r} for mission {mission_key!r}")

