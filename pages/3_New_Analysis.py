"""New Analysis — reset any previous run and begin a fresh guided analysis."""

import streamlit as st

from utils.file_io import new_run_id
from utils.session_state import init_session_state, reset_session_state, safe_page_link

# Initialize session state schema defaults
init_session_state()

st.title("New Analysis")
st.write(
    "Starting a new analysis clears any previous mission, grid, training "
    "run, and results from this session."
)

# Display notice if an existing analysis run is currently active in session state
if st.session_state.get("run_id"):
    st.info(f"An analysis is already in progress (run `{st.session_state['run_id']}`).")
    safe_page_link("pages/4_Mission_Selection.py", label="Continue Existing Analysis", icon=":material/flag:")
    st.divider()

# Primary action button to clear all session state data and assign a new unique run ID
if st.button("Start Fresh Analysis", type="primary", icon=":material/add_circle:"):
    reset_session_state()
    st.session_state["run_id"] = new_run_id()
    st.rerun()
