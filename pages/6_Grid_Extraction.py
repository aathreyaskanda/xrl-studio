"""Grid Extraction — OpenCV pipeline turning the uploaded image into an occupancy grid."""

import streamlit as st

from rl.environment import OBSTACLE
from utils.constants import DEFAULT_GRID_COLS, DEFAULT_GRID_ROWS
from utils.session_state import init_session_state, mark_step_complete, require_step, safe_page_link
from vision.grid_extractor import GridExtractionConfig, GridExtractor
from vision.image_loader import ImageLoadError, load_image

init_session_state()

st.title("Grid Extraction")

if not require_step("upload_layout"):
    st.stop()

st.write("Configure how the uploaded layout is converted into a discrete occupancy grid.")

col1, col2, col3 = st.columns(3)
with col1:
    grid_rows = st.number_input("Grid rows", min_value=5, max_value=60, value=DEFAULT_GRID_ROWS)
with col2:
    grid_cols = st.number_input("Grid columns", min_value=5, max_value=60, value=DEFAULT_GRID_COLS)
with col3:
    cell_size = st.slider("Preview Cell Size (px)", 8, 40, 20)

col_thresh, col_inv = st.columns(2)
with col_thresh:
    threshold = st.slider("Binary threshold", 0, 255, 127)
with col_inv:
    invert = st.checkbox("Invert (dark = free space)")

config = GridExtractionConfig(
    grid_rows=int(grid_rows),
    grid_cols=int(grid_cols),
    binary_threshold=int(threshold),
    invert=invert,
)
extractor = GridExtractor(config)

# Live Preview outside the button click block
if st.session_state.get("uploaded_image") is not None:
    try:
        image = load_image(st.session_state["uploaded_image"])
        preview_grid = extractor.extract_occupancy_grid(image)
        preview = extractor.visualize_grid(preview_grid, cell_size=int(cell_size))
        n_obs = int((preview_grid == OBSTACLE).sum())
        st.caption(f"Live preview: {preview_grid.shape[0]}×{preview_grid.shape[1]} cells | {n_obs} obstacles detected")
        st.image(preview, caption="Live Extracted Occupancy Grid")
    except ImageLoadError as error:
        st.error(str(error))

if st.button("Save Extracted Grid", type="primary", icon=":material/grid_view:"):
    try:
        image = load_image(st.session_state["uploaded_image"])
        grid = extractor.extract_occupancy_grid(image)
        st.session_state["occupancy_grid"] = grid
        st.session_state["annotation"] = None
        mark_step_complete("grid_extraction")
        n_obstacles = int((grid == OBSTACLE).sum())
        st.success(f"Grid saved: {grid.shape[0]}×{grid.shape[1]} cells, {n_obstacles} obstacles.")
    except ImageLoadError as error:
        st.error(str(error))

if st.session_state.get("occupancy_grid") is not None:
    safe_page_link("pages/7_Manual_Annotation.py", label="Continue to Manual Annotation", icon=":material/edit:")
