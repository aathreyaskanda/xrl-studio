"""Manual Annotation — mark start, goal, obstacle, and hazard cells on the grid."""

import streamlit as st

from utils.session_state import init_session_state, mark_step_complete, require_step
from vision.annotation import AnnotationManager, AnnotationState
from vision.grid_extractor import GridExtractor

init_session_state()

st.title("✏️ Manual Annotation")

if not require_step("grid_extraction"):
    st.stop()

st.write(
    "Mark the agent's start cell, the goal cell, and any additional "
    "obstacle or hazard cells on top of the extracted grid."
)

grid = st.session_state["occupancy_grid"]
n_rows, n_cols = grid.shape

if not isinstance(st.session_state.get("annotation"), AnnotationState):
    st.session_state["annotation"] = AnnotationState()

manager = AnnotationManager(grid_shape=grid.shape, grid=grid, state=st.session_state["annotation"])

preview = GridExtractor().visualize_grid(grid, annotation=manager.state)
st.image(preview, caption="🟢 start · 🔴 goal · 🟠 hazard · ⬛ obstacle")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Start / Goal")
    default_start = manager.state.start_cell or (0, 0)
    start_row = st.number_input("Start row", min_value=0, max_value=n_rows - 1, value=default_start[0])
    start_col = st.number_input("Start column", min_value=0, max_value=n_cols - 1, value=default_start[1])
    if st.button("Set Start", icon="🟢"):
        manager.set_start((int(start_row), int(start_col)))
        st.rerun()

    default_goal = manager.state.goal_cell or (n_rows - 1, n_cols - 1)
    goal_row = st.number_input("Goal row", min_value=0, max_value=n_rows - 1, value=default_goal[0])
    goal_col = st.number_input("Goal column", min_value=0, max_value=n_cols - 1, value=default_goal[1])
    if st.button("Set Goal", icon="🔴"):
        manager.set_goal((int(goal_row), int(goal_col)))
        st.rerun()

with col2:
    st.subheader("Obstacles / Hazards")
    cell_row = st.number_input("Row", min_value=0, max_value=n_rows - 1, value=0, key="annotate_row")
    cell_col = st.number_input("Column", min_value=0, max_value=n_cols - 1, value=0, key="annotate_col")

    toggle_obstacle_col, toggle_hazard_col = st.columns(2)
    with toggle_obstacle_col:
        if st.button("Toggle Obstacle", icon="⬛"):
            manager.toggle_obstacle((int(cell_row), int(cell_col)))
            st.rerun()
    with toggle_hazard_col:
        if st.button("Toggle Hazard", icon="🟠"):
            manager.toggle_hazard((int(cell_row), int(cell_col)))
            st.rerun()

    if manager.state.obstacle_cells:
        st.caption(f"Manual obstacles: {sorted(manager.state.obstacle_cells)}")
    if manager.state.hazard_cells:
        st.caption(f"Hazards: {sorted(manager.state.hazard_cells)}")

st.divider()

errors = manager.validate()
if errors:
    for error in errors:
        st.error(error)
else:
    st.success("Annotation is valid — start and goal are set and clear of obstacles.")

if st.button("Save Annotation", type="primary", icon="✅", disabled=bool(errors)):
    st.session_state["annotation"] = manager.state
    mark_step_complete("manual_annotation")
    st.success("Annotation saved.")
    st.page_link("pages/8_Reward_Configuration.py", label="Continue to Reward Configuration", icon="⚙️")
