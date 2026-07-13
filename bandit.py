"""
Contextual Thompson Sampling router.

We keep one Beta(alpha, beta) distribution per (task_type, arm) pair.
This is the simplest form of "context" — condition the bandit on
task type instead of treating all queries as one giant undifferentiated
stream. It's enough to demonstrate real contextual routing without
needing embeddings/LinUCB (that's the stretch goal, noted at the bottom).
"""

import random
from models import ARMS, TASK_TYPES


class ThompsonRouter:
    def __init__(self):
        # alpha/beta priors per (task_type, arm) — start at 1,1 (uniform)
        self.alpha = {t: {a: 1.0 for a in ARMS} for t in TASK_TYPES}
        self.beta = {t: {a: 1.0 for a in ARMS} for t in TASK_TYPES}

    def select_arm(self, task_type: str) -> str:
        samples = {
            a: random.betavariate(self.alpha[task_type][a], self.beta[task_type][a])
            for a in ARMS
        }
        return max(samples, key=samples.get)

    def update(self, task_type: str, arm: str, reward_signal: float):
        """reward_signal in [0, 1] — we treat it as a pseudo-success probability
        (reward already folds in accuracy, cost, latency; we squash it to [0,1]
        via a sigmoid-ish clip before feeding the Beta update)."""
        r = max(0.0, min(1.0, reward_signal))
        self.alpha[task_type][arm] += r
        self.beta[task_type][arm] += (1 - r)
