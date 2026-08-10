"""Behaviour Analysis — coverage, loops, reward concentration, and state revisits."""

import streamlit as st

from analytics.coverage import coverage_over_time
from analytics.loop_detection import detect_loops
from analytics.reward_concentration import compute_reward_concentration
from analytics.state_revisit import compute_state_revisit_frequency
from utils.session_state import init_session_state, mark_step_complete, require_step

init_session_state()

st.title("🔍 Behaviour Analysis")

if not require_step("training"):
    st.stop()

logger = st.session_state["training_logs"]
grid = st.session_state["occupancy_grid"]

tab_coverage, tab_loops, tab_concentration, tab_revisit = st.tabs(
    ["Coverage", "Loop Detection", "Reward Concentration", "State Revisit"]
)

with tab_coverage:
    try:
        st.write(coverage_over_time(logger, grid.size))
    except NotImplementedError:
        st.info("Not implemented yet — see `analytics/coverage.py`.")

with tab_loops:
    try:
        st.write([detect_loops(episode) for episode in logger.get_logs()])
    except NotImplementedError:
        st.info("Not implemented yet — see `analytics/loop_detection.py`.")

with tab_concentration:
    try:
        st.write(compute_reward_concentration(logger))
    except NotImplementedError:
        st.info("Not implemented yet — see `analytics/reward_concentration.py`.")

with tab_revisit:
    try:
        st.write(compute_state_revisit_frequency(logger, grid.shape))
    except NotImplementedError:
        st.info("Not implemented yet — see `analytics/state_revisit.py`.")

st.divider()
if st.button("Mark Behaviour Analysis Reviewed", type="primary", icon="🚨"):
    mark_step_complete("behaviour_analysis")
    st.success("Marked complete.")
    st.page_link("pages/11_Reward_Hacking_Detection.py", label="Continue to Reward Hacking Detection", icon="🚨")
