"""Behaviour logging captured during training, feeding all downstream analytics."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from utils.file_io import save_json


@dataclass
class EpisodeLog:
    """A single training episode's trajectory and outcome."""

    episode: int
    total_reward: float
    steps: int
    visited_states: list[int] = field(default_factory=list)
    actions: list[int] = field(default_factory=list)
    rewards: list[float] = field(default_factory=list)
    epsilon: float = 0.0
    reached_goal: bool = False


class TrainingLogger:
    """Accumulates :class:`EpisodeLog` entries across a training run."""

    def __init__(self) -> None:
        self.episodes: list[EpisodeLog] = []

    def start_episode(self, episode: int) -> EpisodeLog:
        """Begin tracking a new episode and return its log entry."""
        # Instantiates a fresh EpisodeLog container and appends to episode history list
        log_entry = EpisodeLog(episode=episode, total_reward=0.0, steps=0)
        self.episodes.append(log_entry)
        return log_entry

    def log_step(self, log_entry: EpisodeLog, state: int, action: int, reward: float) -> None:
        """Record a single environment step against an episode log."""
        # Append state, action, and reward transition values to per-step lists
        log_entry.visited_states.append(state)
        log_entry.actions.append(action)
        log_entry.rewards.append(reward)
        log_entry.total_reward += reward
        log_entry.steps += 1

    def get_logs(self) -> list[EpisodeLog]:
        """Return all recorded episode logs."""
        return self.episodes

    def export_json(self, path: Path) -> Path:
        """Serialize all episode logs to a JSON file."""
        # Convert dataclass instances to dict via vars() for JSON serialization
        payload = {"episodes": [vars(log) for log in self.episodes]}
        return save_json(payload, path)

    def export_csv(self, path: Path) -> Path:
        """Serialize per-episode summary metrics (episode, reward, steps) to CSV."""
        import pandas as pd

        # Extract per-episode summary records for tabular pandas DataFrame export
        records = [
            {
                "episode": ep.episode,
                "total_reward": ep.total_reward,
                "steps": ep.steps,
                "epsilon": ep.epsilon,
                "reached_goal": ep.reached_goal,
            }
            for ep in self.episodes
        ]
        df = pd.DataFrame(records)
        path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(path, index=False)
        return path
