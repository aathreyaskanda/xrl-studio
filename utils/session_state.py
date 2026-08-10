"""Centralized Streamlit session-state management.

Every key the app reads or writes across pages is declared here, with a
single source of truth for defaults and reset behavior. Pages should
prefer these helpers over touching ``st.session_state`` directly, so the
schema stays easy to reason about as the application grows.
"""

from __future__ import annotations

from typing import Any, Callable

import streamlit as st

from utils.constants import WIZARD_STEPS

# Default values for every key tracked in session state. Mutable defaults
# (e.g. sets) are wrapped in a zero-arg callable so each session gets its
# own fresh instance instead of sharing one across users/reruns.
_DEFAULTS: dict[str, Any | Callable[[], Any]] = {
    "mission_profile": None,      # benchmarks.mission_profiles.MissionProfile | None
    "uploaded_image": None,       # bytes | None — raw uploaded file bytes
    "occupancy_grid": None,       # numpy.ndarray | None
    "annotation": None,           # vision.annotation.AnnotationState | None
    "reward_config": None,        # rl.reward_presets.RewardConfig | None
    "trained_agent": None,        # rl.q_learning.QLearningAgent | None
    "training_logs": None,        # rl.training_logger.TrainingLogger | None
    "hacking_report": None,       # analytics.hacking_detector.RewardHackingReport | None
    "llm_summary": None,          # str | None
    "completed_steps": lambda: set(),   # set[str] — subset of WIZARD_STEPS
    "run_id": None,                # str | None — unique id for the current analysis
}


def init_session_state() -> None:
    """Populate any missing session-state keys with their default value.

    Safe to call on every page render; existing values are left untouched.
    """
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = default() if callable(default) else default


def reset_session_state() -> None:
    """Clear all analysis state to start a fresh run (used by New Analysis)."""
    for key, default in _DEFAULTS.items():
        st.session_state[key] = default() if callable(default) else default


def mark_step_complete(step: str) -> None:
    """Record that a wizard step has been completed."""
    if step not in WIZARD_STEPS:
        raise ValueError(f"Unknown wizard step: {step!r}")
    st.session_state.setdefault("completed_steps", set()).add(step)


def is_step_complete(step: str) -> bool:
    """Check whether a wizard step has already been completed."""
    return step in st.session_state.get("completed_steps", set())


def require_step(step: str) -> bool:
    """Guard a page behind a prerequisite wizard step.

    Renders a warning and a link back to Home if the prerequisite has not
    been completed yet. Returns True if the page should continue
    rendering its normal content.
    """
    if is_step_complete(step):
        return True

    st.warning(
        f"This step requires **{step.replace('_', ' ').title()}** to be "
        "completed first. Please go back and finish the previous step."
    )
    st.page_link("pages/1_Home.py", label="Back to Home", icon="🏠")
    return False
