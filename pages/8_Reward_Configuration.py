"""Reward Configuration — review and tune the mission's reward preset."""

import streamlit as st

from rl.reward_presets import RewardConfig
from utils.session_state import init_session_state, mark_step_complete, require_step

init_session_state()

st.title("⚙️ Reward Configuration")

if not require_step("manual_annotation"):
    st.stop()

mission = st.session_state["mission_profile"]
preset = mission.reward_config

st.write(f"Default reward preset for **{mission.display_name}**. Adjust if needed, then confirm.")

goal_reward = st.slider("Goal reward", 0.0, 30.0, preset.goal_reward)
step_penalty = st.slider("Step penalty", -1.0, 0.0, preset.step_penalty)
collision_penalty = st.slider("Collision penalty", -5.0, 0.0, preset.collision_penalty)
revisit_penalty = st.slider("Revisit penalty", -1.0, 0.0, preset.revisit_penalty)
coverage_bonus = st.slider("Coverage bonus", 0.0, 2.0, preset.coverage_bonus)
hazard_penalty = st.slider("Hazard penalty", -5.0, 0.0, preset.hazard_penalty)

if st.button("Confirm Reward Configuration", type="primary", icon="✅"):
    st.session_state["reward_config"] = RewardConfig(
        goal_reward=goal_reward,
        step_penalty=step_penalty,
        collision_penalty=collision_penalty,
        revisit_penalty=revisit_penalty,
        coverage_bonus=coverage_bonus,
        hazard_penalty=hazard_penalty,
    )
    mark_step_complete("reward_configuration")
    st.success("Reward configuration saved.")
    st.page_link("pages/9_Train_Agent.py", label="Continue to Train Q-learning", icon="🏋️")
