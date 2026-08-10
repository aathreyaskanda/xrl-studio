"""LLM Summary — Gemini-generated natural-language explanation of the run."""

import streamlit as st

from reports.gemini_summary import build_prompt, generate_summary
from utils.config import is_gemini_configured
from utils.session_state import init_session_state, mark_step_complete, require_step

init_session_state()

st.title("🤖 LLM Summary")

if not require_step("explainability_dashboard"):
    st.stop()

if not is_gemini_configured():
    st.warning(
        "No Gemini API key configured. Add `GEMINI_API_KEY` to "
        "`.streamlit/secrets.toml` or your environment to enable this step."
    )

report = st.session_state["hacking_report"]
mission = st.session_state["mission_profile"]

context = {
    "mission_name": mission.display_name if mission else "the mission",
    "metrics": {
        "coverage_score": getattr(report, "coverage_score", None),
        "is_hacking_suspected": getattr(report, "is_hacking_suspected", None),
    },
}

with st.expander("Preview prompt sent to Gemini"):
    st.code(build_prompt(context))

if st.button("Generate Summary", type="primary", icon="🤖", disabled=not is_gemini_configured()):
    try:
        summary = generate_summary(context)
        st.session_state["llm_summary"] = summary
        mark_step_complete("llm_summary")
        st.success("Summary generated.")
    except NotImplementedError:
        st.info(
            "Gemini summary generation is not implemented yet — see "
            "`reports/gemini_summary.py` and PROJECT_PLAN.md, Phase 8."
        )
    except RuntimeError as error:
        st.error(str(error))

if st.session_state.get("llm_summary"):
    st.markdown("### Summary")
    st.write(st.session_state["llm_summary"])
    st.page_link("pages/14_Download_Report.py", label="Continue to Download Report", icon="📄")
