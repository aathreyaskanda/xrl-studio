"""Home — landing page and entry point into the guided analysis flow."""

import streamlit as st

from utils.constants import APP_NAME, APP_TAGLINE, APP_VERSION
from utils.session_state import init_session_state, safe_page_link

# Initialize session state schema defaults
init_session_state()

# Display application header title and subtitle tagline
st.title(APP_NAME)
st.caption(APP_TAGLINE)

st.markdown(
    """
XRL Studio trains a simple reinforcement learning agent on a grid-world
version of a real-world mission — then explains **what it actually
learned**, including whether it found a shortcut that games its reward
function instead of solving the task.
"""
)

# 3-column navigation hub cards for quick landing page entry
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Learn")
    st.write("New to reward hacking? Start with a short conceptual primer.")
    safe_page_link("pages/2_Learn.py", label="Go to Learn", icon=":material/menu_book:")
with col2:
    st.subheader("New Analysis")
    st.write("Upload a layout, train an agent, and inspect its behaviour.")
    safe_page_link("pages/3_New_Analysis.py", label="Start New Analysis", icon=":material/add_circle:")
with col3:
    st.subheader("Explainability")
    st.write("Once trained, dig into heatmaps, charts, and the policy inspector.")
    safe_page_link("pages/12_Explainability_Dashboard.py", label="View Dashboard", icon=":material/monitoring:")

st.divider()
st.caption(f"Version {APP_VERSION}.")
