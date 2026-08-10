"""Detection of repetitive movement loops, a common reward-hacking symptom."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from rl.training_logger import EpisodeLog


@dataclass
class LoopEvent:
    """A detected cycle of revisited states within a single episode."""

    episode: int
    cycle_states: list[int]
    repeat_count: int


def detect_loops(episode_log: EpisodeLog, min_cycle_length: int = 2, max_cycle_length: int = 10) -> list[LoopEvent]:
    """Find repeated state cycles within one episode's trajectory."""
    states = episode_log.visited_states
    n = len(states)
    loops: list[LoopEvent] = []
    if n < min_cycle_length * 2:
        return loops

    i = 0
    while i < n - min_cycle_length * 2 + 1:
        found_loop = False
        for cycle_len in range(min_cycle_length, min(max_cycle_length + 1, (n - i) // 2 + 1)):
            pattern = states[i : i + cycle_len]
            # Count consecutive repetitions of pattern
            repeats = 1
            j = i + cycle_len
            while j + cycle_len <= n and states[j : j + cycle_len] == pattern:
                repeats += 1
                j += cycle_len

            req_repeats = 3 if cycle_len == 2 else 2
            if repeats >= req_repeats:
                loops.append(
                    LoopEvent(
                        episode=episode_log.episode,
                        cycle_states=pattern,
                        repeat_count=repeats,
                    )
                )
                i = j  # Skip ahead past the loop
                found_loop = True
                break

        if not found_loop:
            i += 1

    return loops


def loop_density_grid(episode_logs: list[EpisodeLog], grid_shape: tuple[int, int]) -> np.ndarray:
    """Aggregate loop activity per cell across episodes, for the Loop Density heatmap."""
    density = np.zeros(grid_shape, dtype=float)
    n_cols = grid_shape[1]

    for ep in episode_logs:
        loops = detect_loops(ep)
        for loop in loops:
            for state in loop.cycle_states:
                row, col = divmod(state, n_cols)
                if 0 <= row < grid_shape[0] and 0 <= col < grid_shape[1]:
                    density[row, col] += loop.repeat_count

    return density

