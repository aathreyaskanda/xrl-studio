"""New Analysis — reset any previous run and begin a fresh guided analysis."""

import streamlit as st

from utils.file_io import new_run_id
from utils.session_state import init_session_state, reset_session_state

init_session_state()

st.title("🆕 New Analysis")
st.write(
    "Starting a new analysis clears any previous mission, grid, training "
    "run, and results from this session."
)

if st.session_state.get("run_id"):
    st.info(f"An analysis is already in progress (run `{st.session_state['run_id']}`).")
    st.page_link("pages/4_Mission_Selection.py", label="Continue Existing Analysis", icon="🎯")
    st.divider()

if st.button("Start Fresh Analysis", type="primary", icon="🆕"):
    reset_session_state()
    st.session_state["run_id"] = new_run_id()
    st.rerun()
