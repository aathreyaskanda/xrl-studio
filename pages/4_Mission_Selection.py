"""Mission Selection — choose which mission profile drives labels and reward presets."""

import streamlit as st

from benchmarks.benchmark_library import list_benchmarks
from benchmarks.mission_profiles import list_mission_profiles
from utils.session_state import init_session_state, mark_step_complete, safe_page_link

# Initialize session state schema defaults
init_session_state()

st.title("Mission Selection")
st.write(
    "Pick a mission profile. This only changes labels and reward presets "
    "— the RL engine is identical across missions."
)

# Fetch available registered mission profiles list
profiles = list_mission_profiles()
labels = [profile.display_name for profile in profiles]
current = st.session_state.get("mission_profile")
default_index = profiles.index(current) if current in profiles else 0

# Radio button selector for mission profile choice
selected_label = st.radio("Choose a mission:", labels, index=default_index)
selected_profile = profiles[labels.index(selected_label)]

# Display active mission profile details and label mapping expander
st.info(selected_profile.description)
with st.expander("Labels used in this mission"):
    st.write(f"- Agent: **{selected_profile.agent_label}**")
    st.write(f"- Goal: **{selected_profile.goal_label}**")
    st.write(f"- Obstacle: **{selected_profile.obstacle_label}**")
    st.write(f"- Hazard: **{selected_profile.hazard_label}**")

# Display pre-built benchmark layouts available for the selected mission profile
benchmarks = list_benchmarks(selected_profile.key)
if benchmarks:
    with st.expander(f"Pre-built benchmarks for {selected_profile.display_name} ({len(benchmarks)})"):
        for bm in benchmarks:
            st.markdown(f"**{bm.name}** ({bm.grid_shape[0]}x{bm.grid_shape[1]} grid)")
            st.caption(bm.description)

# Commit mission choice to session state and mark wizard step as complete
if st.button("Confirm Mission", type="primary", icon=":material/check_circle:"):
    st.session_state["mission_profile"] = selected_profile
    mark_step_complete("mission_selection")
    st.success(f"Mission set to {selected_profile.display_name}.")
    safe_page_link("pages/5_Upload_Layout.py", label="Continue to Upload / Select Layout", icon=":material/image:")
