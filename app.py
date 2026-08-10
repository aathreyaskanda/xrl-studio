"""
XRL Studio — Explainable Reinforcement Learning System for Reward Hacking Detection.

This is the application entry point. It wires together the Streamlit
multipage navigation, applies global configuration/theming, and
initializes session state shared across all pages.

Run with:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from utils.config import ensure_runtime_directories
from utils.constants import APP_ICON, APP_NAME, APP_TAGLINE
from utils.session_state import init_session_state


def _load_custom_css() -> None:
    """Inject the shared stylesheet, if present."""
    css_path = "assets/styles/custom.css"
    try:
        with open(css_path, "r", encoding="utf-8") as css_file:
            st.markdown(f"<style>{css_file.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Styling is a progressive enhancement; the app must still run without it.
        pass


def build_navigation():
    """Declare every page in the application flow, in wizard order."""
    pages = {
        "Overview": [
            st.Page("pages/1_Home.py", title="Home", icon="🏠", default=True),
            st.Page("pages/2_Learn.py", title="Learn", icon="📖"),
        ],
        "New Analysis": [
            st.Page("pages/3_New_Analysis.py", title="New Analysis", icon="🆕"),
            st.Page("pages/4_Mission_Selection.py", title="Mission Selection", icon="🎯"),
            st.Page("pages/5_Upload_Layout.py", title="Upload Layout", icon="🖼️"),
            st.Page("pages/6_Grid_Extraction.py", title="Grid Extraction", icon="🧩"),
            st.Page("pages/7_Manual_Annotation.py", title="Manual Annotation", icon="✏️"),
            st.Page("pages/8_Reward_Configuration.py", title="Reward Configuration", icon="⚙️"),
            st.Page("pages/9_Train_Agent.py", title="Train Q-learning", icon="🏋️"),
        ],
        "Results": [
            st.Page("pages/10_Behaviour_Analysis.py", title="Behaviour Analysis", icon="🔍"),
            st.Page("pages/11_Reward_Hacking_Detection.py", title="Reward Hacking Detection", icon="🚨"),
            st.Page("pages/12_Explainability_Dashboard.py", title="Explainability Dashboard", icon="📊"),
            st.Page("pages/13_LLM_Summary.py", title="LLM Summary", icon="🤖"),
            st.Page("pages/14_Download_Report.py", title="Download Report", icon="📄"),
        ],
    }
    return st.navigation(pages)


def main() -> None:
    st.set_page_config(
        page_title=APP_NAME,
        page_icon=APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    ensure_runtime_directories()
    init_session_state()
    _load_custom_css()

    with st.sidebar:
        st.markdown(f"### {APP_ICON} {APP_NAME}")
        st.caption(APP_TAGLINE)
        st.divider()

    navigation = build_navigation()
    navigation.run()


if __name__ == "__main__":
    main()
