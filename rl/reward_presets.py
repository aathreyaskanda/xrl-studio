"""Reward configuration shared by the RL engine and mission profiles.

Mission profiles only change labels and which :class:`RewardConfig` is
selected — the environment and agent implementation are identical
across every mission.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RewardConfig:
    """Reward-shaping parameters consumed by ``rl.environment.GridWorldEnv``."""

    goal_reward: float = 10.0
    step_penalty: float = -0.05
    collision_penalty: float = -1.0
    revisit_penalty: float = -0.1
    coverage_bonus: float = 0.2
    hazard_penalty: float = -2.0


# Default presets, keyed by mission profile key. Values are placeholders to
# be tuned once training is implemented — see PROJECT_PLAN.md, Phase 3.
MISSION_REWARD_PRESETS: dict[str, RewardConfig] = {
    "warehouse_inspection": RewardConfig(goal_reward=10.0, coverage_bonus=0.3),
    "hospital_delivery": RewardConfig(goal_reward=15.0, collision_penalty=-2.0),
    "indoor_security_patrol": RewardConfig(goal_reward=8.0, coverage_bonus=0.5),
    "industrial_facility_inspection": RewardConfig(goal_reward=10.0, hazard_penalty=-3.0),
    "search_rescue": RewardConfig(goal_reward=20.0, step_penalty=-0.02),
}


def get_reward_preset(mission_key: str) -> RewardConfig:
    """Look up the default reward preset for a mission, by key.

    Raises:
        KeyError: if ``mission_key`` has no registered preset.
    """
    try:
        return MISSION_REWARD_PRESETS[mission_key]
    except KeyError as exc:
        raise KeyError(f"No reward preset registered for mission: {mission_key!r}") from exc
