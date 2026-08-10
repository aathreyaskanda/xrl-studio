"""Learn — conceptual primer on reward hacking in reinforcement learning."""

import streamlit as st

from benchmarks.mission_profiles import list_mission_profiles
from utils.session_state import init_session_state

init_session_state()

st.title("📖 Learn: Reward Hacking in Reinforcement Learning")

st.markdown(
    """
### What is reward hacking?

Reward hacking happens when an RL agent finds a way to maximize its
reward signal without actually accomplishing the task designer's
intent — exploiting a loophole in the reward function rather than
solving the real problem.

### What XRL Studio looks for

| Signal | What it means |
|---|---|
| **Low coverage** | The agent ignores most of the map, focusing on a small area. |
| **Loop density** | The agent repeats the same short cycle of moves instead of exploring. |
| **Reward concentration** | Most reward comes from a tiny number of states/actions. |
| **State revisit frequency** | The agent revisits the same cells far more than expected. |

### The benchmark library

Each mission profile below only changes labels and reward presets — the
underlying grid-world engine and Q-learning algorithm stay the same,
which makes it easy to compare behaviour across missions.
"""
)

st.subheader("Mission Profiles")
for profile in list_mission_profiles():
    with st.expander(f"{profile.icon} {profile.display_name}"):
        st.write(profile.description)

st.divider()
st.page_link("pages/3_New_Analysis.py", label="Start a New Analysis", icon="🆕")
