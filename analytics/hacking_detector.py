"""Aggregates individual analytics signals into a single reward-hacking verdict."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from rl.training_logger import TrainingLogger


@dataclass
class RewardHackingReport:
    """Consolidated output of the Reward Hacking Detection step."""

    is_hacking_suspected: bool = False
    coverage_score: float = 0.0
    reward_concentration: dict = field(default_factory=dict)
    loop_events: list = field(default_factory=list)
    revisit_grid: np.ndarray | None = None
    notes: list[str] = field(default_factory=list)


def detect_reward_hacking(logger: TrainingLogger, grid_shape: tuple[int, int]) -> RewardHackingReport:
    """Run all analytics detectors and combine them into one report.

    Orchestrates ``analytics.coverage``, ``analytics.loop_detection``,
    ``analytics.reward_concentration``, and ``analytics.state_revisit``.

    TODO(analytics): implement once the individual detectors are done.
    See PROJECT_PLAN.md, Phase 4-5.
    """
    raise NotImplementedError("detect_reward_hacking is not yet implemented.")
