"""Runtime configuration: secrets/environment access and filesystem setup."""

from __future__ import annotations

import os

import streamlit as st

from utils.constants import RUNTIME_DIRS


def ensure_runtime_directories() -> None:
    """Create the generated/ and exports/ subdirectories if they don't exist."""
    for directory in RUNTIME_DIRS:
        directory.mkdir(parents=True, exist_ok=True)


def get_gemini_api_key() -> str | None:
    """Resolve the Gemini API key from Streamlit secrets or the environment.

    Checks ``st.secrets["GEMINI_API_KEY"]`` first (recommended for
    deployment), then falls back to the ``GEMINI_API_KEY`` environment
    variable (convenient for local development).
    """
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return str(st.secrets["GEMINI_API_KEY"])
    except FileNotFoundError:
        # No .streamlit/secrets.toml present; fall back to the environment.
        pass
    return os.environ.get("GEMINI_API_KEY")


def is_gemini_configured() -> bool:
    """Whether a Gemini API key is available for the LLM Summary step."""
    return bool(get_gemini_api_key())
