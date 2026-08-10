"""Grid Extraction — OpenCV pipeline turning the uploaded image into an occupancy grid."""

import streamlit as st

from rl.environment import OBSTACLE
from utils.constants import DEFAULT_GRID_COLS, DEFAULT_GRID_ROWS
from utils.session_state import init_session_state, mark_step_complete, require_step
from vision.grid_extractor import GridExtractionConfig, GridExtractor
from vision.image_loader import ImageLoadError, load_image

init_session_state()

st.title("🧩 Grid Extraction")

if not require_step("upload_layout"):
    st.stop()

st.write("Configure how the uploaded layout is converted into a discrete occupancy grid.")

col1, col2 = st.columns(2)
with col1:
    grid_rows = st.number_input("Grid rows", min_value=5, max_value=60, value=DEFAULT_GRID_ROWS)
with col2:
    grid_cols = st.number_input("Grid columns", min_value=5, max_value=60, value=DEFAULT_GRID_COLS)

threshold = st.slider("Binary threshold", 0, 255, 127)
invert = st.checkbox("Invert (dark = free space)")

if st.button("Extract Grid", type="primary", icon="🧩"):
    config = GridExtractionConfig(
        grid_rows=int(grid_rows),
        grid_cols=int(grid_cols),
        binary_threshold=int(threshold),
        invert=invert,
    )
    extractor = GridExtractor(config)
    try:
        image = load_image(st.session_state["uploaded_image"])
        grid = extractor.extract_occupancy_grid(image)
        st.session_state["occupancy_grid"] = grid
        # A new grid invalidates any prior annotation drawn against the old shape/obstacles.
        st.session_state["annotation"] = None
        mark_step_complete("grid_extraction")
        n_obstacles = int((grid == OBSTACLE).sum())
        st.success(f"Grid extracted: {grid.shape[0]}×{grid.shape[1]} cells, {n_obstacles} marked as obstacles.")
    except ImageLoadError as error:
        st.error(str(error))

if st.session_state.get("occupancy_grid") is not None:
    grid = st.session_state["occupancy_grid"]
    preview = GridExtractor().visualize_grid(grid)
    st.image(preview, caption=f"Extracted grid preview ({grid.shape[0]}×{grid.shape[1]})")
    st.page_link("pages/7_Manual_Annotation.py", label="Continue to Manual Annotation", icon="✏️")
