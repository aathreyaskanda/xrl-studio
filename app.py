"""
XRL Studio — Explainable Reinforcement Learning System for Reward Hacking Detection.

This is the application entry point. It wires together top-level navigation,
applies the theme and design system, and manages session state across all pages.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from utils.config import ensure_runtime_directories
from utils.constants import APP_NAME, APP_TAGLINE, APP_VERSION
from utils.session_state import init_session_state
from utils.theme import init_theme_state, inject_theme_css, toggle_theme


def build_navigation():
    """Declare every page in the application flow with top-level navigation."""
    # Define multipage hierarchy grouped into 3 top-level navbar sections:
    # 1. Overview (Home, Learn)
    # 2. New Analysis (Guided Wizard steps 3-9)
    # 3. Results (Analytics & Output steps 10-14)
    pages = {
        "Overview": [
            st.Page("pages/1_Home.py", title="Home", icon=":material/home:", default=True),
            st.Page("pages/2_Learn.py", title="Learn", icon=":material/menu_book:"),
        ],
        "New Analysis": [
            st.Page("pages/3_New_Analysis.py", title="New Analysis", icon=":material/add_circle:"),
            st.Page("pages/4_Mission_Selection.py", title="Mission Selection", icon=":material/flag:"),
            st.Page("pages/5_Upload_Layout.py", title="Upload Layout", icon=":material/image:"),
            st.Page("pages/6_Grid_Extraction.py", title="Grid Extraction", icon=":material/grid_view:"),
            st.Page("pages/7_Manual_Annotation.py", title="Manual Annotation", icon=":material/edit:"),
            st.Page("pages/8_Reward_Configuration.py", title="Reward Configuration", icon=":material/tune:"),
            st.Page("pages/9_Train_Agent.py", title="Train Q-learning", icon=":material/model_training:"),
        ],
        "Results": [
            st.Page("pages/10_Behaviour_Analysis.py", title="Behaviour Analysis", icon=":material/search_insights:"),
            st.Page("pages/11_Reward_Hacking_Detection.py", title="Reward Hacking Detection", icon=":material/report:"),
            st.Page("pages/12_Explainability_Dashboard.py", title="Explainability Dashboard", icon=":material/monitoring:"),
            st.Page("pages/13_LLM_Summary.py", title="LLM Summary", icon=":material/smart_toy:"),
            st.Page("pages/14_Download_Report.py", title="Download Report", icon=":material/description:"),
        ],
    }
    # Position="top" places primary menu bar at the top of the viewport
    return st.navigation(pages, position="top")


def main() -> None:
    # Set page title, browser tab icon, wide layout mode, and initial sidebar state
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=":material/psychology:",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    # Ensure all required export/generated directories exist on local filesystem
    ensure_runtime_directories()
    # Initialize session state schema with single-source-of-truth defaults
    init_session_state()
    # Initialize dark/light mode theme selection and inject custom CSS tokens
    init_theme_state()
    inject_theme_css()

    # Contextual Sidebar Panel: holds branding title, theme toggle, and active session run info
    with st.sidebar:
        st.markdown(f"### {APP_NAME}")
        st.caption(APP_TAGLINE)
        st.divider()

        # Theme mode toggle switch callback control
        current_theme = st.session_state.get("theme_mode", "dark")
        st.toggle(
            "Dark Mode",
            value=(current_theme == "dark"),
            key="theme_toggle_switch",
            on_change=toggle_theme,
        )

        st.divider()
        st.caption("Active Session Context")
        run_id = st.session_state.get("run_id")
        mission = st.session_state.get("mission_profile")
        if run_id:
            st.text(f"Run ID: {run_id}")
        if mission:
            st.text(f"Mission: {mission.display_name}")

    # Build and execute navigation router
    navigation = build_navigation()
    navigation.run()


if __name__ == "__main__":
    main()
