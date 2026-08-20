"""Tabular Q-learning agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np

from rl.environment import GridWorldEnv
from rl.training_logger import TrainingLogger


@dataclass
class QLearningConfig:
    """Hyperparameters for tabular Q-learning."""

    # Learning rate (alpha): controls how much new info overrides old Q-value
    learning_rate: float = 0.1
    # Discount factor (gamma): controls importance of future vs immediate rewards
    discount_factor: float = 0.95
    # Initial exploration rate (epsilon) for epsilon-greedy selection
    epsilon_start: float = 1.0
    # Minimum exploration floor below which epsilon will not decay
    epsilon_min: float = 0.05
    # Multiplicative decay rate per episode (epsilon = epsilon * epsilon_decay)
    epsilon_decay: float = 0.995
    # Total episodes to run during training
    episodes: int = 500


class QLearningAgent:
    """Epsilon-greedy tabular Q-learning agent over a discrete state space."""

    def __init__(self, n_states: int, n_actions: int, config: QLearningConfig | None = None) -> None:
        self.n_states = n_states
        self.n_actions = n_actions
        self.config = config or QLearningConfig()
        # Initialize 2D Q-table with zeros (n_states rows x n_actions columns)
        self.q_table = np.zeros((n_states, n_actions), dtype=np.float32)
        # Set initial epsilon exploration parameter
        self.epsilon = self.config.epsilon_start

    def select_action(self, state: int, *, greedy: bool = False) -> int:
        """Choose an action via epsilon-greedy exploration."""
        # Exploitation: pick highest Q-value action (with random tie-breaking) if greedy=True or rand() >= epsilon
        if greedy or np.random.rand() >= self.epsilon:
            q_values = self.q_table[state]
            max_val = np.max(q_values)
            # Find all action indices sharing the maximum Q-value to tie-break uniformly
            best_actions = np.flatnonzero(q_values == max_val)
            return int(np.random.choice(best_actions))
        # Exploration: choose random action uniformly across action space
        return int(np.random.randint(self.n_actions))

    def update(self, state: int, action: int, reward: float, next_state: int, done: bool) -> None:
        """Apply the Q-learning (Bellman) update rule to a single transition."""
        # Terminal state target is just the immediate reward; non-terminal includes discounted max future Q
        if done:
            target = reward
        else:
            target = reward + self.config.discount_factor * np.max(self.q_table[next_state])

        # Temporal Difference (TD) error: difference between target estimate and current Q-value
        td_error = target - self.q_table[state, action]
        # Update rule: Q(s, a) = Q(s, a) + alpha * TD_error
        self.q_table[state, action] += self.config.learning_rate * td_error

    def train(
        self,
        env: GridWorldEnv,
        logger: TrainingLogger | None = None,
        progress_callback: Callable[[int, int, float, float], None] | None = None,
    ) -> TrainingLogger:
        """Run the full training loop for ``self.config.episodes`` episodes."""
        if logger is None:
            logger = TrainingLogger()

        self.epsilon = self.config.epsilon_start

        # Episode iteration loop
        for episode in range(1, self.config.episodes + 1):
            obs, info = env.reset()
            ep_log = logger.start_episode(episode)
            ep_log.epsilon = self.epsilon
            ep_log.visited_states.append(obs)

            done = False
            # Step loop within episode until termination or max step truncation
            while not done:
                # Epsilon-greedy action selection
                action = self.select_action(obs, greedy=False)
                next_obs, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated

                # Perform Bellman Q-table update
                self.update(obs, action, reward, next_obs, done)
                # Log step details to training logger
                logger.log_step(ep_log, obs, action, reward)

                if terminated and info.get("reached_goal"):
                    ep_log.reached_goal = True

                obs = next_obs

            # Multiplicative epsilon decay at episode end, bounded by epsilon_min
            self.epsilon = max(self.config.epsilon_min, self.epsilon * self.config.epsilon_decay)

            # Trigger progress updates (used by Streamlit UI progress bar)
            if progress_callback is not None:
                progress_callback(episode, self.config.episodes, ep_log.total_reward, self.epsilon)

        return logger

    def get_policy(self) -> np.ndarray:
        """Return the greedy action for every state, shape ``(n_states,)``."""
        # Find index of maximum Q-value along action axis for each state
        return np.argmax(self.q_table, axis=1)

    def get_q_table(self) -> np.ndarray:
        """Return the full Q-table, shape ``(n_states, n_actions)``."""
        return self.q_table
