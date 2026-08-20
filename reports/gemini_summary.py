"""Natural-language summary generation via the Gemini Flash API."""

from __future__ import annotations

from typing import Any

from utils.config import get_gemini_api_key, is_gemini_configured

# Preferred primary Gemini model name
GEMINI_MODEL_NAME = "gemini-3.6-flash"
# Model candidates fallback order list
GEMINI_MODEL_FALLBACKS = [
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-2.0-flash",
    "gemini-flash-latest",
]

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
    # Format metrics dictionary items into a bulleted list string
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
        RuntimeError: if no Gemini API key is configured or API call fails.
    """
    # Guard against invocation without an active API key
    if not is_gemini_configured():
        raise RuntimeError(
            "No Gemini API key configured. Set GEMINI_API_KEY in "
            ".streamlit/secrets.toml or as an environment variable."
        )

    import google.generativeai as genai

    # Configure global API key
    api_key = get_gemini_api_key()
    genai.configure(api_key=api_key)

    prompt = build_prompt(context)

    last_error: Exception | None = None

    # Try preferred candidate model names sequentially
    for model_name in GEMINI_MODEL_FALLBACKS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            if hasattr(response, "text") and response.text:
                return response.text.strip()
        except Exception as error:
            last_error = error
            continue

    # Fallback to dynamic model discovery if configured static candidate list fails
    try:
        for m in genai.list_models():
            if "generateContent" in getattr(m, "supported_generation_methods", []):
                model_name = m.name.replace("models/", "")
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    if hasattr(response, "text") and response.text:
                        return response.text.strip()
                except Exception as error:
                    last_error = error
                    continue
    except Exception:
        pass

    raise RuntimeError(f"Gemini API request failed: {last_error}")
