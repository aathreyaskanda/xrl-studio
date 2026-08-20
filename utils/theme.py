"""Dark/light theme state management and dynamic CSS injection."""

from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

THEME_KEY = "theme_mode"  # "dark" | "light"
DEFAULT_THEME = "dark"


def init_theme_state() -> None:
    """Ensure a theme choice exists in session state (call once per page render)."""
    if THEME_KEY not in st.session_state:
        st.session_state[THEME_KEY] = DEFAULT_THEME


def toggle_theme() -> None:
    """Flip the current theme between 'dark' and 'light'."""
    current = st.session_state.get(THEME_KEY, DEFAULT_THEME)
    st.session_state[THEME_KEY] = "light" if current == "dark" else "dark"


def inject_theme_css(css_path: str = "assets/styles/custom.css") -> None:
    """Load the global stylesheet and inject theme variables based on active session state."""
    theme = st.session_state.get(THEME_KEY, DEFAULT_THEME)
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
    except FileNotFoundError:
        css_content = ""

    # Inject CSS stylesheet
    st.markdown(f"<style>\n{css_content}\n</style>", unsafe_allow_html=True)

    # Inject JavaScript theme switcher silently via component iframe
    js_code = f"""
    <script>
    const el = window.parent.document.querySelector('.stApp');
    if (el) {{
        el.setAttribute('data-xrl-theme', '{theme}');
    }}
    </script>
    """
    components.html(js_code, height=0, width=0)
