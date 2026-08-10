"""Explainability Dashboard — heatmaps, charts, trajectory replay, and policy inspector."""

import numpy as np
import streamlit as st

from analytics.state_revisit import compute_state_revisit_frequency
from rl.environment import OBSTACLE

from utils.constants import ACTIONS, CHART_TYPES, HEATMAP_TYPES
from utils.session_state import init_session_state, mark_step_complete, require_step
from visualization.charts import CHART_RENDERERS
from visualization.heatmaps import HEATMAP_RENDERERS
from visualization.policy_inspector import action_to_arrow, build_policy_table
from visualization.trajectory_replay import TrajectoryReplay

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
    episodes = logger.get_logs()
    if not episodes:
        st.warning("No training episodes recorded in logger.")
    else:
        ep_options = {
            ep.episode: f"Episode {ep.episode} ({ep.steps} steps, total reward: {ep.total_reward:.2f})"
            for ep in episodes
        }
        selected_ep_num = st.selectbox(
            "Select Episode to Replay",
            list(ep_options.keys()),
            index=len(episodes) - 1,
            format_func=lambda ep_id: ep_options[ep_id],
        )
        selected_ep = next(ep for ep in episodes if ep.episode == selected_ep_num)

        replay = TrajectoryReplay(grid, selected_ep)
        total_frames = replay.total_frames()

        if total_frames == 0:
            st.warning("Selected episode has no recorded frames.")
        else:
            step = st.slider("Step Scrubber", min_value=0, max_value=total_frames - 1, value=total_frames - 1)

            fig = replay.render_plotly_frame(step)
            st.plotly_chart(fig, use_container_width=True)

            m1, m2, m3, m4 = st.columns(4)
            agent_st = selected_ep.visited_states[step]
            agent_pos = divmod(agent_st, grid.shape[1])
            m1.metric("Current Position", f"{agent_pos}")

            if step > 0 and step - 1 < len(selected_ep.actions):
                act_idx = selected_ep.actions[step - 1]
                action_name = ACTIONS[act_idx].capitalize()
                action_arrow = action_to_arrow(act_idx)
                act_display = f"{action_name} ({action_arrow})"
            else:
                act_display = "Start"

            m2.metric("Action Taken", act_display)

            step_reward = (
                selected_ep.rewards[step - 1]
                if step > 0 and step - 1 < len(selected_ep.rewards)
                else 0.0
            )
            m3.metric("Step Reward", f"{step_reward:.2f}")

            cum_reward = sum(selected_ep.rewards[:step])
            m4.metric("Cumulative Reward", f"{cum_reward:.2f}")

with policy_tab:
    agent = st.session_state.get("trained_agent")
    if agent is None:
        st.warning("No trained agent found in session state.")
    else:
        visit_counts = compute_state_revisit_frequency(logger, grid.shape)
        reward_per_cell = np.zeros(grid.shape, dtype=float)
        cols = grid.shape[1]
        for ep in logger.get_logs():
            for state, r in zip(ep.visited_states, ep.rewards):
                row, col = divmod(state, cols)
                if 0 <= row < grid.shape[0] and 0 <= col < grid.shape[1]:
                    reward_per_cell[row, col] += r

        policy_df = build_policy_table(agent, grid, visit_counts, reward_per_cell)

        st.caption("Tabular inspection of learned Q-values, visit counts, and policy direction per cell.")

        p1, p2, p3 = st.columns(3)
        visited_cells = int((visit_counts > 0).sum())
        p1.metric("Visited Grid Cells", f"{visited_cells} / {grid.size}")

        q_max = float(np.max(agent.get_q_table()))
        p2.metric("Max Learned Q-Value", f"{q_max:.2f}")

        free_cells = int((grid != OBSTACLE).sum())
        p3.metric("Free Grid Space", f"{free_cells} cells")

        st.dataframe(policy_df, use_container_width=True, hide_index=True)

        st.download_button(
            "📥 Export Policy Table (CSV)",
            data=policy_df.to_csv(index=False),
            file_name="policy_inspector_table.csv",
            mime="text/csv",
        )



st.divider()
if st.button("Continue to LLM Summary", type="primary", icon="🤖"):
    mark_step_complete("explainability_dashboard")
    st.page_link("pages/13_LLM_Summary.py", label="LLM Summary", icon="🤖")

