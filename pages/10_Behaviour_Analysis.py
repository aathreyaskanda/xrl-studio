import numpy as np
import pandas as pd
import streamlit as st

from analytics.coverage import compute_coverage, coverage_over_time
from analytics.loop_detection import detect_loops, loop_density_grid
from analytics.reward_concentration import compute_reward_concentration
from analytics.state_revisit import compute_state_revisit_frequency
from rl.environment import OBSTACLE
from utils.session_state import init_session_state, mark_step_complete, require_step

init_session_state()

st.title("🔍 Behaviour Analysis")

if not require_step("training"):
    st.stop()

logger = st.session_state["training_logs"]
grid = st.session_state["occupancy_grid"]
navigable_count = int(np.count_nonzero(grid != OBSTACLE)) if grid is not None else grid.size

tab_coverage, tab_loops, tab_concentration, tab_revisit = st.tabs(
    ["📊 Coverage", "🔄 Loop Detection", "⚖️ Reward Concentration", "🗺️ State Revisit"]
)

with tab_coverage:
    st.subheader("Navigable Grid Coverage")
    cov_series = coverage_over_time(logger, navigable_count)

    if len(cov_series) > 0:
        final_cov = cov_series[-1] * 100
        max_cov = float(np.max(cov_series)) * 100
    else:
        final_cov, max_cov = 0.0, 0.0

    c1, c2, c3 = st.columns(3)
    c1.metric("Final Cumulative Coverage", f"{final_cov:.1f}%")
    c2.metric("Peak Coverage Achieved", f"{max_cov:.1f}%")
    c3.metric("Navigable Cells", f"{navigable_count}")

    st.caption("Cumulative fraction of navigable grid cells visited across training episodes.")
    if len(cov_series) > 0:
        st.line_chart(pd.DataFrame({"Cumulative Coverage (%)": cov_series * 100}))

with tab_loops:
    st.subheader("Repetitive Trajectory Loops")
    all_loops: list[dict] = []
    for ep_log in logger.get_logs():
        loops = detect_loops(ep_log)
        for l in loops:
            all_loops.append({
                "Episode": l.episode,
                "Cycle Length": len(l.cycle_states),
                "Repeats": l.repeat_count,
                "Cycle States": str(l.cycle_states),
            })

    episodes_with_loops = len({l["Episode"] for l in all_loops})
    total_loops = len(all_loops)
    max_repeats = max((l["Repeats"] for l in all_loops), default=0)

    l1, l2, l3 = st.columns(3)
    l1.metric("Total Loop Events", f"{total_loops}")
    l2.metric("Episodes with Loops", f"{episodes_with_loops}")
    l3.metric("Max Loop Repetitions", f"{max_repeats}")

    if total_loops > 0:
        st.warning(f"Detected {total_loops} repeating loop events across {episodes_with_loops} episodes.")
        st.dataframe(pd.DataFrame(all_loops), use_container_width=True)
    else:
        st.success("No repetitive movement loops detected in training trajectories.")

with tab_concentration:
    st.subheader("Reward Concentration (Gini Index)")
    conc = compute_reward_concentration(logger)

    gini = conc["gini_coefficient"]
    top_share = conc["top_10pct_share"] * 100
    unique_rewarded = int(conc["unique_states_rewarded"])
    total_pos_reward = conc["total_positive_reward"]

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("Gini Coefficient", f"{gini:.3f}")
    r2.metric("Top 10% Cell Share", f"{top_share:.1f}%")
    r3.metric("Unique Rewarded Cells", f"{unique_rewarded}")
    r4.metric("Total Positive Reward", f"{total_pos_reward:.1f}")

    if gini > 0.6:
        st.warning("High reward concentration (Gini > 0.6). The agent is concentrating reward collection in a narrow subset of cells, which may indicate reward hacking.")
    else:
        st.info("Reward distribution across states is relatively balanced.")

with tab_revisit:
    st.subheader("Cell Revisit Counts")
    revisit_grid = compute_state_revisit_frequency(logger, grid.shape)

    max_visits = int(np.max(revisit_grid))
    avg_visits = float(np.mean(revisit_grid[grid != OBSTACLE])) if navigable_count > 0 else 0.0
    total_visits = int(np.sum(revisit_grid))

    v1, v2, v3 = st.columns(3)
    v1.metric("Max Cell Visits", f"{max_visits}")
    v2.metric("Avg Visits per Free Cell", f"{avg_visits:.1f}")
    v3.metric("Total Grid Steps", f"{total_visits}")

    st.caption("Visits matrix per cell coordinates (row x col):")
    st.dataframe(pd.DataFrame(revisit_grid), use_container_width=True)

st.divider()
if st.button("Mark Behaviour Analysis Reviewed", type="primary", icon="🚨"):
    mark_step_complete("behaviour_analysis")
    st.success("Marked complete.")
    st.page_link("pages/11_Reward_Hacking_Detection.py", label="Continue to Reward Hacking Detection", icon="🚨")

