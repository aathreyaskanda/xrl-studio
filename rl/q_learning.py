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

    learning_rate: float = 0.1
    discount_factor: float = 0.95
    epsilon_start: float = 1.0
    epsilon_min: float = 0.05
    epsilon_decay: float = 0.995
    episodes: int = 500


class QLearningAgent:
    """Epsilon-greedy tabular Q-learning agent over a discrete state space.

    TODO(rl): implement ``select_action``, ``update``, and ``train``.
    See PROJECT_PLAN.md, Phase 3.
    """

    def __init__(self, n_states: int, n_actions: int, config: QLearningConfig | None = None) -> None:
        self.n_states = n_states
        self.n_actions = n_actions
        self.config = config or QLearningConfig()
        self.q_table = np.zeros((n_states, n_actions), dtype=np.float32)
        self.epsilon = self.config.epsilon_start

    def select_action(self, state: int, *, greedy: bool = False) -> int:
        """Choose an action via epsilon-greedy exploration."""
        if greedy or np.random.rand() >= self.epsilon:
            q_values = self.q_table[state]
            max_val = np.max(q_values)
            best_actions = np.flatnonzero(q_values == max_val)
            return int(np.random.choice(best_actions))
        return int(np.random.randint(self.n_actions))

    def update(self, state: int, action: int, reward: float, next_state: int, done: bool) -> None:
        """Apply the Q-learning (Bellman) update rule to a single transition."""
        if done:
            target = reward
        else:
            target = reward + self.config.discount_factor * np.max(self.q_table[next_state])

        td_error = target - self.q_table[state, action]
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

        for episode in range(1, self.config.episodes + 1):
            obs, info = env.reset()
            ep_log = logger.start_episode(episode)
            ep_log.epsilon = self.epsilon
            ep_log.visited_states.append(obs)

            done = False
            while not done:
                action = self.select_action(obs, greedy=False)
                next_obs, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated

                self.update(obs, action, reward, next_obs, done)
                logger.log_step(ep_log, obs, action, reward)

                if terminated and info.get("reached_goal"):
                    ep_log.reached_goal = True

                obs = next_obs

            self.epsilon = max(self.config.epsilon_min, self.epsilon * self.config.epsilon_decay)

            if progress_callback is not None:
                progress_callback(episode, self.config.episodes, ep_log.total_reward, self.epsilon)

        return logger

    def get_policy(self) -> np.ndarray:
        """Return the greedy action for every state, shape ``(n_states,)``."""
        return np.argmax(self.q_table, axis=1)

    def get_q_table(self) -> np.ndarray:
        """Return the full Q-table, shape ``(n_states, n_actions)``."""
        return self.q_table
