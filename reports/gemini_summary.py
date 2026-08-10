"""Natural-language summary generation via the Gemini Flash API."""

from __future__ import annotations

from typing import Any

from utils.config import get_gemini_api_key, is_gemini_configured

GEMINI_MODEL_NAME = "gemini-1.5-flash"

SUMMARY_PROMPT_TEMPLATE = """\
You are an assistant explaining a reinforcement learning agent's behaviour
during a {mission_name} simulation to a non-expert reader.

Metrics:
{metrics_block}

Write a concise, plain-language summary covering:
1. What the agent learned to do.
2. Whether reward hacking was detected, and what form it took.
3. Concrete recommendations to fix the reward function or environment.
"""


def build_prompt(context: dict[str, Any]) -> str:
    """Fill :data:`SUMMARY_PROMPT_TEMPLATE` from a run's analysis context."""
    metrics_block = "\n".join(f"- {key}: {value}" for key, value in context.get("metrics", {}).items())
    return SUMMARY_PROMPT_TEMPLATE.format(
        mission_name=context.get("mission_name", "the mission"),
        metrics_block=metrics_block or "(no metrics available)",
    )


def generate_summary(context: dict[str, Any]) -> str:
    """Call the Gemini Flash API to produce the LLM Summary step's output.

    Args:
        context: Analysis context (mission name, metrics, hacking report,
            etc.) as assembled by the LLM Summary page.

    Returns:
        The generated summary text.

    Raises:
        RuntimeError: if no Gemini API key is configured.

    TODO(reports): implement the actual API call using
    ``google-generativeai``. See PROJECT_PLAN.md, Phase 8.
    """
    if not is_gemini_configured():
        raise RuntimeError(
            "No Gemini API key configured. Set GEMINI_API_KEY in "
            ".streamlit/secrets.toml or as an environment variable."
        )
    raise NotImplementedError("generate_summary is not yet implemented.")
