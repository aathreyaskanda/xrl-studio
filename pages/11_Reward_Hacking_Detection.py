"""Reward Hacking Detection — aggregate verdict from all behaviour analytics."""

import streamlit as st

from analytics.hacking_detector import detect_reward_hacking
from utils.session_state import init_session_state, mark_step_complete, require_step

init_session_state()

st.title("🚨 Reward Hacking Detection")

if not require_step("behaviour_analysis"):
    st.stop()

logger = st.session_state["training_logs"]
grid = st.session_state["occupancy_grid"]

if st.button("Run Detection", type="primary", icon="🚨"):
    try:
        report = detect_reward_hacking(logger, grid.shape)
        st.session_state["hacking_report"] = report
        mark_step_complete("hacking_detection")
        verdict = "⚠️ Reward hacking suspected" if report.is_hacking_suspected else "✅ No reward hacking detected"
        st.subheader(verdict)
        st.page_link(
            "pages/12_Explainability_Dashboard.py",
            label="Continue to Explainability Dashboard",
            icon="📊",
        )
    except NotImplementedError:
        st.info(
            "Reward hacking detection is not implemented yet — see "
            "`analytics/hacking_detector.py` and PROJECT_PLAN.md, Phase 5."
        )
