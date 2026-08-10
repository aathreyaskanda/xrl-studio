"""Mission profile definitions.

A mission profile only changes labels and which reward preset is used —
the RL engine (environment + agent) is identical across all missions.
"""

from __future__ import annotations

from dataclasses import dataclass

from rl.reward_presets import RewardConfig, get_reward_preset


@dataclass(frozen=True)
class MissionProfile:
    """Display metadata and reward wiring for one mission type."""

    key: str
    display_name: str
    description: str
    icon: str
    agent_label: str
    goal_label: str
    obstacle_label: str
    hazard_label: str

    @property
    def reward_config(self) -> RewardConfig:
        """The reward preset registered for this mission."""
        return get_reward_preset(self.key)


MISSION_PROFILES: dict[str, MissionProfile] = {
    "warehouse_inspection": MissionProfile(
        key="warehouse_inspection",
        display_name="Warehouse Inspection",
        description="An autonomous agent inspects shelving rows in a warehouse.",
        icon="📦",
        agent_label="Inspector Robot",
        goal_label="Inspection Point",
        obstacle_label="Shelf",
        hazard_label="Spill Zone",
    ),
    "hospital_delivery": MissionProfile(
        key="hospital_delivery",
        display_name="Hospital Delivery",
        description="An autonomous agent delivers supplies between hospital wards.",
        icon="🏥",
        agent_label="Delivery Robot",
        goal_label="Ward",
        obstacle_label="Wall",
        hazard_label="Restricted Area",
    ),
    "indoor_security_patrol": MissionProfile(
        key="indoor_security_patrol",
        display_name="Indoor Security Patrol",
        description="An autonomous agent patrols an indoor facility for security coverage.",
        icon="🛡️",
        agent_label="Patrol Robot",
        goal_label="Checkpoint",
        obstacle_label="Barrier",
        hazard_label="Blind Spot",
    ),
    "industrial_facility_inspection": MissionProfile(
        key="industrial_facility_inspection",
        display_name="Industrial Facility Inspection",
        description="An autonomous agent inspects equipment across an industrial facility.",
        icon="🏭",
        agent_label="Inspection Drone",
        goal_label="Equipment Station",
        obstacle_label="Machinery",
        hazard_label="Hazard Zone",
    ),
    "search_rescue": MissionProfile(
        key="search_rescue",
        display_name="Search & Rescue",
        description="An autonomous agent searches a disaster site for survivors.",
        icon="🚨",
        agent_label="Rescue Robot",
        goal_label="Survivor Location",
        obstacle_label="Debris",
        hazard_label="Structural Hazard",
    ),
}


def get_mission_profile(key: str) -> MissionProfile:
    """Look up a mission profile by key.

    Raises:
        KeyError: if ``key`` has no registered profile.
    """
    try:
        return MISSION_PROFILES[key]
    except KeyError as exc:
        raise KeyError(f"No mission profile registered for: {key!r}") from exc


def list_mission_profiles() -> list[MissionProfile]:
    """Return all registered mission profiles, in a stable display order."""
    return list(MISSION_PROFILES.values())
