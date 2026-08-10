"""Train Q-learning — run tabular Q-learning on the configured GridWorld."""

import streamlit as st

from rl.environment import EnvironmentConfig, GridWorldEnv
from rl.q_learning import QLearningAgent, QLearningConfig
from rl.training_logger import TrainingLogger
from utils.session_state import init_session_state, mark_step_complete, require_step

init_session_state()

st.title("🏋️ Train Q-learning")

if not require_step("reward_configuration"):
    st.stop()

st.write("Configure training hyperparameters, then run tabular Q-learning on the annotated grid.")

col1, col2 = st.columns(2)
with col1:
    episodes = st.slider("Episodes", 50, 2000, 500, step=50)
    learning_rate = st.slider("Learning rate", 0.01, 1.0, 0.1)
with col2:
    discount_factor = st.slider("Discount factor", 0.5, 0.999, 0.95)
    epsilon_start = st.slider("Initial exploration (epsilon)", 0.0, 1.0, 1.0)

if st.button("Start Training", type="primary", icon="🏋️"):
    grid = st.session_state["occupancy_grid"]
    annotation = st.session_state["annotation"]
    reward_config = st.session_state["reward_config"]

    env_config = EnvironmentConfig(
        grid=grid,
        start_pos=annotation.start_cell,
        goal_pos=annotation.goal_cell,
        reward_config=reward_config,
        hazard_cells=annotation.hazard_cells,
    )
    agent_config = QLearningConfig(
        learning_rate=learning_rate,
        discount_factor=discount_factor,
        epsilon_start=epsilon_start,
        episodes=int(episodes),
    )

    env = GridWorldEnv(env_config)
    agent = QLearningAgent(n_states=grid.size, n_actions=4, config=agent_config)
    logger = TrainingLogger()

    progress_bar = st.progress(0.0)
    status_text = st.empty()

    def update_progress(current_ep: int, total_eps: int, total_reward: float, eps_val: float) -> None:
        frac = current_ep / total_eps
        progress_bar.progress(frac)
        status_text.text(
            f"Episode {current_ep}/{total_eps} | Reward: {total_reward:.2f} | Epsilon: {eps_val:.3f}"
        )

    with st.spinner("Training agent..."):
        logger = agent.train(env, logger, progress_callback=update_progress)

    st.session_state["trained_agent"] = agent
    st.session_state["training_logs"] = logger
    mark_step_complete("training")
    st.success("Training complete!")
    st.page_link("pages/10_Behaviour_Analysis.py", label="Continue to Behaviour Analysis", icon="🔍")

