import pandas as pd
import streamlit as st

from analytics.hacking_detector import detect_reward_hacking
from utils.session_state import init_session_state, mark_step_complete, require_step

init_session_state()

st.title("🚨 Reward Hacking Detection")

if not require_step("behaviour_analysis"):
    st.stop()

logger = st.session_state["training_logs"]
grid = st.session_state["occupancy_grid"]

report = st.session_state.get("hacking_report")

if report is None:
    report = detect_reward_hacking(logger, grid.shape, occupancy_grid=grid)
    st.session_state["hacking_report"] = report
    mark_step_complete("hacking_detection")

if st.button("Re-run Detection Analysis", type="secondary", icon="🔄"):
    report = detect_reward_hacking(logger, grid.shape, occupancy_grid=grid)
    st.session_state["hacking_report"] = report
    mark_step_complete("hacking_detection")
    st.rerun()

if report is not None:
    if report.is_hacking_suspected:
        st.error("⚠️ **Verdict: REWARD HACKING SUSPECTED**")
    else:
        st.success("✅ **Verdict: CLEAN RUN — NO REWARD HACKING DETECTED**")

    st.subheader("Diagnostic Evidence & Key Indicators")
    c1, c2, c3 = st.columns(3)
    c1.metric("Coverage Score", f"{report.coverage_score:.1%}")
    c2.metric("Gini Concentration", f"{report.reward_concentration.get('gini_coefficient', 0.0):.3f}")
    c3.metric("Total Loop Events", f"{len(report.loop_events)}")

    st.markdown("### 📋 Automated Inspection Findings")
    for note in report.notes:
        if report.is_hacking_suspected:
            st.write(f"- ⚠️ {note}")
        else:
            st.write(f"- ✅ {note}")

    with st.expander("🔍 Detailed Analytical Evidence"):
        st.write("**Reward Concentration Summary:**", report.reward_concentration)
        if report.loop_events:
            st.write("**Detected Loop Events:**")
            st.dataframe(
                pd.DataFrame([
                    {
                        "Episode": l.episode,
                        "Cycle Length": len(l.cycle_states),
                        "Repeats": l.repeat_count,
                        "States": str(l.cycle_states),
                    }
                    for l in report.loop_events
                ]),
                use_container_width=True,
            )

    with st.expander("⚔️ Normal vs. Flawed Reward Comparison (Side-by-Side Analysis)"):
        st.caption("Compare how a balanced reward setup vs. a flawed reward function behaves under the same grid layout.")
        if st.button("Run Side-by-Side Comparison", icon="⚖️"):
            from rl.environment import EnvironmentConfig, GridWorldEnv
            from rl.q_learning import QLearningAgent, QLearningConfig
            from rl.reward_presets import RewardConfig
            from visualization.heatmaps import plot_reward_heatmap

            start_pos = st.session_state.get("start_cell", (0, 0))
            goal_pos = st.session_state.get("goal_cell", (grid.shape[0] - 1, grid.shape[1] - 1))

            with st.spinner("Running twin simulations for comparative analysis..."):
                # 1. Normal/Balanced Run
                cfg_normal = EnvironmentConfig(
                    grid=grid,
                    start_pos=start_pos,
                    goal_pos=goal_pos,
                    reward_config=RewardConfig(step_penalty=-0.01, goal_reward=10.0, coverage_bonus=0.5, revisit_penalty=-0.2),
                    max_steps=100,
                )
                env_normal = GridWorldEnv(cfg_normal)
                agent_normal = QLearningAgent(env_normal.observation_space.n, env_normal.action_space.n, QLearningConfig(episodes=50))
                logger_normal = agent_normal.train(env_normal)
                report_normal = detect_reward_hacking(logger_normal, grid.shape, occupancy_grid=grid)

                # 2. Flawed/Hacked Run (Positive revisit penalty = positive feedback loop for re-visiting)
                cfg_flawed = EnvironmentConfig(
                    grid=grid,
                    start_pos=start_pos,
                    goal_pos=goal_pos,
                    reward_config=RewardConfig(step_penalty=0.0, goal_reward=0.0, coverage_bonus=0.0, revisit_penalty=1.0),
                    max_steps=100,
                )
                env_flawed = GridWorldEnv(cfg_flawed)
                agent_flawed = QLearningAgent(env_flawed.observation_space.n, env_flawed.action_space.n, QLearningConfig(episodes=50))
                logger_flawed = agent_flawed.train(env_flawed)
                report_flawed = detect_reward_hacking(logger_flawed, grid.shape, occupancy_grid=grid)

            col_norm, col_flaw = st.columns(2)

            with col_norm:
                st.subheader("🟢 Normal (Balanced Reward)")
                if report_normal.is_hacking_suspected:
                    st.warning("⚠️ Hacking Flagged")
                else:
                    st.success("✅ Clean Run")
                st.metric("Coverage Score", f"{report_normal.coverage_score:.1%}")
                st.metric("Gini Concentration", f"{report_normal.reward_concentration.get('gini_coefficient', 0.0):.3f}")
                fig_norm = plot_reward_heatmap(grid, logger_normal)
                st.plotly_chart(fig_norm, use_container_width=True)

            with col_flaw:
                st.subheader("🔴 Flawed (Hacked Reward)")
                if report_flawed.is_hacking_suspected:
                    st.error("⚠️ REWARD HACKING SUSPECTED")
                else:
                    st.info("Clean Run")
                st.metric("Coverage Score", f"{report_flawed.coverage_score:.1%}")
                st.metric("Gini Concentration", f"{report_flawed.reward_concentration.get('gini_coefficient', 0.0):.3f}")
                fig_flaw = plot_reward_heatmap(grid, logger_flawed)
                st.plotly_chart(fig_flaw, use_container_width=True)


    st.divider()
    st.page_link(
        "pages/12_Explainability_Dashboard.py",
        label="Continue to Explainability Dashboard",
        icon="📊",
    )

