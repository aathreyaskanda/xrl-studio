"""Manual Annotation — interactive floor plan annotation with click-to-annotate, tools, and undo."""

import copy
import numpy as np
import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates

from utils.session_state import init_session_state, mark_step_complete, require_step, safe_page_link
from vision.annotation import AnnotationManager, AnnotationState
from vision.canvas_utils import pixel_to_cell
from vision.grid_extractor import GridExtractor

init_session_state()

st.title("Manual Annotation")

if not require_step("grid_extraction"):
    st.stop()

st.write(
    "Click directly on the grid preview to place start/goal positions or toggle obstacle and hazard cells."
)

grid = st.session_state.get("occupancy_grid")
if grid is None:
    st.info("Occupancy grid not found. Please complete the Grid Extraction step first.")
    st.stop()
    grid = np.zeros((1, 1), dtype=int)
n_rows, n_cols = grid.shape

if not isinstance(st.session_state.get("annotation"), AnnotationState):
    st.session_state["annotation"] = AnnotationState()

if "annotation_history" not in st.session_state:
    st.session_state["annotation_history"] = []

manager = AnnotationManager(grid_shape=grid.shape, grid=grid, state=st.session_state["annotation"])

# Toolbar controls
col_tool, col_zoom, col_undo, col_clear = st.columns([3, 2, 1, 1])

with col_tool:
    active_tool = st.radio(
        "Annotation Tool",
        ["Start", "Goal", "Obstacle", "Hazard", "Erase"],
        horizontal=True,
    )

with col_zoom:
    cell_size = st.slider("Zoom (cell size px)", 10, 40, 20)

with col_undo:
    st.write("")
    st.write("")
    if st.button("Undo", icon=":material/undo:", disabled=len(st.session_state["annotation_history"]) == 0):
        if st.session_state["annotation_history"]:
            st.session_state["annotation"] = st.session_state["annotation_history"].pop()
            st.rerun()

with col_clear:
    st.write("")
    st.write("")
    if st.button("Clear", icon=":material/delete:"):
        st.session_state["annotation_history"].append(copy.deepcopy(manager.state))
        st.session_state["annotation"] = AnnotationState()
        st.rerun()

# Render interactive image canvas
preview_img = GridExtractor().visualize_grid(grid, annotation=manager.state, cell_size=int(cell_size))

st.caption("Click on any cell in the canvas below:")
click_data = streamlit_image_coordinates(preview_img, key="annotation_canvas")

if click_data is not None:
    click_x, click_y = click_data["x"], click_data["y"]
    row, col = pixel_to_cell(click_x, click_y, cell_size_px=int(cell_size))

    if 0 <= row < n_rows and 0 <= col < n_cols:
        last_click = st.session_state.get("_last_canvas_click")
        current_click_key = (click_x, click_y, active_tool)

        if last_click != current_click_key:
            st.session_state["_last_canvas_click"] = current_click_key
            st.session_state["annotation_history"].append(copy.deepcopy(manager.state))

            cell = (row, col)
            if active_tool == "Start":
                manager.set_start(cell)
            elif active_tool == "Goal":
                manager.set_goal(cell)
            elif active_tool == "Obstacle":
                manager.toggle_obstacle(cell)
            elif active_tool == "Hazard":
                manager.toggle_hazard(cell)
            elif active_tool == "Erase":
                if manager.state.start_cell == cell:
                    manager.state.start_cell = None
                if manager.state.goal_cell == cell:
                    manager.state.goal_cell = None
                if cell in manager.state.obstacle_cells:
                    manager.state.obstacle_cells.remove(cell)
                if cell in manager.state.hazard_cells:
                    manager.state.hazard_cells.remove(cell)

            st.session_state["annotation"] = manager.state
            st.rerun()

st.divider()

# Secondary coordinate precision fallback
with st.expander("Precise Coordinate Entry Fallback"):
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Start / Goal")
        default_start = manager.state.start_cell or (0, 0)
        start_row = st.number_input("Start row", min_value=0, max_value=n_rows - 1, value=default_start[0])
        start_col = st.number_input("Start column", min_value=0, max_value=n_cols - 1, value=default_start[1])
        if st.button("Set Start (Manual)", icon=":material/place:"):
            st.session_state["annotation_history"].append(copy.deepcopy(manager.state))
            manager.set_start((int(start_row), int(start_col)))
            st.session_state["annotation"] = manager.state
            st.rerun()

        default_goal = manager.state.goal_cell or (n_rows - 1, n_cols - 1)
        goal_row = st.number_input("Goal row", min_value=0, max_value=n_rows - 1, value=default_goal[0])
        goal_col = st.number_input("Goal column", min_value=0, max_value=n_cols - 1, value=default_goal[1])
        if st.button("Set Goal (Manual)", icon=":material/flag:"):
            st.session_state["annotation_history"].append(copy.deepcopy(manager.state))
            manager.set_goal((int(goal_row), int(goal_col)))
            st.session_state["annotation"] = manager.state
            st.rerun()

    with col2:
        st.subheader("Obstacles / Hazards")
        cell_row = st.number_input("Row", min_value=0, max_value=n_rows - 1, value=0, key="annotate_row")
        cell_col = st.number_input("Column", min_value=0, max_value=n_cols - 1, value=0, key="annotate_col")

        toggle_obs_col, toggle_haz_col = st.columns(2)
        with toggle_obs_col:
            if st.button("Toggle Obstacle (Manual)", icon=":material/block:"):
                st.session_state["annotation_history"].append(copy.deepcopy(manager.state))
                manager.toggle_obstacle((int(cell_row), int(cell_col)))
                st.session_state["annotation"] = manager.state
                st.rerun()
        with toggle_haz_col:
            if st.button("Toggle Hazard (Manual)", icon=":material/warning:"):
                st.session_state["annotation_history"].append(copy.deepcopy(manager.state))
                manager.toggle_hazard((int(cell_row), int(cell_col)))
                st.session_state["annotation"] = manager.state
                st.rerun()

if manager.state.obstacle_cells:
    st.caption(f"Manual obstacles ({len(manager.state.obstacle_cells)}): {sorted(manager.state.obstacle_cells)}")
if manager.state.hazard_cells:
    st.caption(f"Hazards ({len(manager.state.hazard_cells)}): {sorted(manager.state.hazard_cells)}")

st.divider()

errors = manager.validate()
if errors:
    for error in errors:
        st.error(error)
else:
    st.success("Annotation is valid — start and goal are set and clear of obstacles.")

if st.button("Save Annotation", type="primary", icon=":material/check_circle:", disabled=bool(errors)):
    st.session_state["annotation"] = manager.state
    mark_step_complete("manual_annotation")
    st.success("Annotation saved.")
    safe_page_link("pages/8_Reward_Configuration.py", label="Continue to Reward Configuration", icon=":material/tune:")
