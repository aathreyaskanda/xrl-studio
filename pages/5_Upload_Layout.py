"""Upload or Select Layout — upload a layout image or choose a pre-built benchmark."""

import streamlit as st

from benchmarks.benchmark_library import list_benchmarks
from utils.session_state import init_session_state, mark_step_complete, require_step, safe_page_link
from vision.grid_extractor import GridExtractor
from vision.image_loader import ImageLoadError, load_image

# Initialize session state schema defaults
init_session_state()

st.title("Upload or Select Layout")

# Guard page behind prerequisite mission_selection step requirement
if not require_step("mission_selection"):
    st.stop()

mission = st.session_state.get("mission_profile")
mission_name = mission.display_name if mission else "Custom Grid"
st.write(f"Mission: **{mission_name}**")

# Tabbed interface: 1. Select Pre-built Benchmark, 2. Upload Custom Image
tab1, tab2 = st.tabs(["Select Pre-built Benchmark", "Upload Custom Image"])

with tab1:
    st.subheader("Pre-built Benchmark Layouts")
    benchmarks = list_benchmarks(mission.key if mission else None)
    if not benchmarks:
        st.info("No pre-built benchmarks available for this mission.")
    else:
        bm_names = [bm.name for bm in benchmarks]
        selected_bm_name = st.selectbox("Choose a benchmark layout:", bm_names)
        selected_bm = next(bm for bm in benchmarks if bm.name == selected_bm_name)

        st.caption(selected_bm.description)
        st.write(
            f"- Grid Size: **{selected_bm.grid_shape[0]} × {selected_bm.grid_shape[1]}**\n"
            f"- Start Cell: `{selected_bm.start_cell}`\n"
            f"- Goal Cell: `{selected_bm.goal_cell}`\n"
            f"- Obstacle Cells: **{len(selected_bm.obstacle_cells)}** | Hazard Cells: **{len(selected_bm.hazard_cells)}**"
        )

        # Generate grid and preview visualization for selected benchmark
        grid = selected_bm.build_grid()
        annotation = selected_bm.build_annotation()
        preview = GridExtractor().visualize_grid(grid, annotation)

        st.image(preview, caption=f"Preview: {selected_bm.name}", use_container_width=True)

        # Load benchmark layout directly into session state and mark pipeline steps complete
        if st.button("Load Benchmark Layout", type="primary", icon=":material/download:"):
            st.session_state["occupancy_grid"] = grid
            st.session_state["annotation"] = annotation
            st.session_state["reward_config"] = mission.reward_config
            mark_step_complete("mission_selection")
            mark_step_complete("upload_layout")
            mark_step_complete("grid_extraction")
            mark_step_complete("manual_annotation")
            st.success(f"Loaded benchmark layout '{selected_bm.name}'!")

            col_a, col_b = st.columns(2)
            with col_a:
                safe_page_link(
                    "pages/8_Reward_Configuration.py",
                    label="Proceed to Reward Configuration",
                    icon=":material/tune:",
                )
            with col_b:
                safe_page_link(
                    "pages/7_Manual_Annotation.py",
                    label="Inspect / Edit Annotations",
                    icon=":material/edit:",
                )

with tab2:
    st.subheader("Upload Custom Top-Down Layout Image")
    # File uploader widget accepting PNG, JPG, JPEG, BMP formats
    uploaded_file = st.file_uploader("Layout image", type=["png", "jpg", "jpeg", "bmp"])

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        try:
            # Validate image decode and dimension constraints before accepting
            load_image(file_bytes)
        except ImageLoadError as error:
            st.error(str(error))
        else:
            st.image(file_bytes, caption="Uploaded layout")
            if st.button("Use This Layout", type="primary", icon=":material/check_circle:"):
                st.session_state["uploaded_image"] = file_bytes
                mark_step_complete("upload_layout")
                st.success("Layout saved to the current analysis.")
                safe_page_link("pages/6_Grid_Extraction.py", label="Continue to Grid Extraction", icon=":material/grid_view:")
    else:
        st.caption("Supported formats: PNG, JPG, JPEG, BMP.")
