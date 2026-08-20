"""Dark/light theme state management and dynamic CSS injection."""

from __future__ import annotations

import streamlit as st

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

    # Streamlit scoping trick: Inject theme root class and scope styles
    theme_css = f"""
    <style>
    {css_content}
    </style>
    <script>
    const el = window.parent.document.querySelector('.stApp');
    if (el) {{
        el.setAttribute('data-xrl-theme', '{theme}');
    }}
    </script>
    """
    st.markdown(theme_css, unsafe_allow_html=True)
