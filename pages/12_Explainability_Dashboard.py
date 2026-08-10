"""Explainability Dashboard — heatmaps, charts, trajectory replay, and policy inspector."""

import streamlit as st

from utils.constants import CHART_TYPES, HEATMAP_TYPES
from utils.session_state import init_session_state, mark_step_complete, require_step
from visualization.charts import CHART_RENDERERS
from visualization.heatmaps import HEATMAP_RENDERERS

init_session_state()

st.title("📊 Explainability Dashboard")

if not require_step("hacking_detection"):
    st.stop()

grid = st.session_state["occupancy_grid"]
report = st.session_state["hacking_report"]
logger = st.session_state["training_logs"]

if report is not None and getattr(report, "is_hacking_suspected", False):
    st.warning("⚠️ Reward hacking was flagged for this run.")

heatmap_tab, chart_tab, replay_tab, policy_tab = st.tabs(
    ["Heatmaps", "Charts", "Trajectory Replay", "Policy Inspector"]
)

with heatmap_tab:
    selected_heatmap = st.selectbox("Heatmap type", HEATMAP_TYPES, format_func=str.title)
    figure = HEATMAP_RENDERERS[selected_heatmap](grid, logger)
    st.plotly_chart(figure, use_container_width=True)

with chart_tab:
    selected_chart = st.selectbox(
        "Chart type", CHART_TYPES, format_func=lambda value: value.replace("_", " ").title()
    )
    figure = CHART_RENDERERS[selected_chart](logger, grid)
    st.plotly_chart(figure, use_container_width=True)

with replay_tab:
    st.info("Trajectory replay is not implemented yet — see `visualization/trajectory_replay.py`.")

with policy_tab:
    st.info("The policy inspector table is not implemented yet — see `visualization/policy_inspector.py`.")

st.divider()
if st.button("Continue to LLM Summary", type="primary", icon="🤖"):
    mark_step_complete("explainability_dashboard")
    st.page_link("pages/13_LLM_Summary.py", label="LLM Summary", icon="🤖")
