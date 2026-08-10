"""LLM Summary — Gemini-generated natural-language explanation of the run."""

import os
import streamlit as st

from reports.gemini_summary import build_prompt, generate_summary
from utils.config import get_gemini_api_key, is_gemini_configured
from utils.session_state import init_session_state, mark_step_complete, require_step

init_session_state()

st.title("🤖 LLM Summary")

if not require_step("explainability_dashboard"):
    st.stop()

# Fallback: allow manual API key entry if not configured in secrets or env
if not is_gemini_configured():
    st.warning(
        "No Gemini API key configured. Add `GEMINI_API_KEY` to "
        "`.streamlit/secrets.toml` or set it below for this session."
    )
    user_api_key = st.text_input("Enter GEMINI_API_KEY", type="password")
    if user_api_key:
        os.environ["GEMINI_API_KEY"] = user_api_key.strip()
        st.success("API key set for this session.")

report = st.session_state.get("hacking_report")
mission = st.session_state.get("mission_profile")
logger = st.session_state.get("training_logs")

episodes = logger.get_logs() if logger else []
last_ep_reward = episodes[-1].total_reward if episodes else 0.0

context = {
    "mission_name": mission.display_name if mission else "the mission",
    "metrics": {
        "coverage_score": f"{getattr(report, 'coverage_score', 0.0):.2%}",
        "is_hacking_suspected": getattr(report, "is_hacking_suspected", False),
        "reward_hacking_findings": "; ".join(getattr(report, "notes", [])) or "None",
        "total_episodes": len(episodes),
        "final_episode_reward": f"{last_ep_reward:.2f}",
    },
}

with st.expander("Preview prompt sent to Gemini"):
    st.code(build_prompt(context))

can_generate = is_gemini_configured()

col_gen1, col_gen2 = st.columns(2)
with col_gen1:
    if st.button("Generate Gemini Summary", type="primary", icon="🤖", disabled=not can_generate):
        try:
            with st.spinner("Generating summary via Gemini Flash..."):
                summary = generate_summary(context)
                st.session_state["llm_summary"] = summary
                mark_step_complete("llm_summary")
                st.success("Summary generated successfully.")
                st.rerun()
        except RuntimeError as error:
            st.error(str(error))

with col_gen2:
    if st.button("Generate Offline Summary", icon="📝"):
        is_hacked = context["metrics"]["is_hacking_suspected"]
        verdict_str = "⚠️ REWARD HACKING SUSPECTED" if is_hacked else "✅ CLEAN RUN — NO REWARD HACKING"
        offline_summary = (
            f"### Automated Executive Summary: {context['mission_name']}\n\n"
            f"**Verdict:** {verdict_str}\n\n"
            f"**Key Metrics:**\n"
            f"- Grid Coverage: {context['metrics']['coverage_score']}\n"
            f"- Total Episodes: {context['metrics']['total_episodes']}\n"
            f"- Final Episode Reward: {context['metrics']['final_episode_reward']}\n\n"
            f"**Inspection Findings:**\n"
            f"{context['metrics']['reward_hacking_findings']}\n"
        )
        st.session_state["llm_summary"] = offline_summary
        mark_step_complete("llm_summary")
        st.success("Offline summary generated.")
        st.rerun()

if st.session_state.get("llm_summary"):
    st.markdown("### Summary")
    st.write(st.session_state["llm_summary"])
    st.divider()
    st.page_link("pages/14_Download_Report.py", label="Continue to Download Report", icon="📄")

