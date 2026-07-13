"""
Mock model 'arms' for BanditRoute.

Each arm has a per-task-type success probability, a token cost,
and a latency profile. No real API calls needed — this lets us
demo the *routing intelligence* without fighting rate limits.

Task types: "code", "math", "qa", "creative"
"""

import random

ARMS = ["phi3_local", "qwen_local", "fireworks_small", "fireworks_large"]

# P(correct answer) per arm per task type — deliberately uneven,
# so there IS something for the bandit to discover.
ACCURACY = {
    "phi3_local":       {"code": 0.55, "math": 0.40, "qa": 0.80, "creative": 0.70},
    "qwen_local":        {"code": 0.82, "math": 0.55, "qa": 0.75, "creative": 0.60},
    "fireworks_small":  {"code": 0.70, "math": 0.85, "qa": 0.78, "creative": 0.72},
    "fireworks_large":  {"code": 0.90, "math": 0.92, "qa": 0.88, "creative": 0.90},
}

# Token cost per query (local = free)
TOKEN_COST = {
    "phi3_local": 0.0,
    "qwen_local": 0.0,
    "fireworks_small": 0.015,   # $ per query, avg
    "fireworks_large": 0.09,
}

# Latency in ms (avg)
LATENCY_MS = {
    "phi3_local": 180,
    "qwen_local": 260,
    "fireworks_small": 400,
    "fireworks_large": 900,
}

TASK_TYPES = ["code", "math", "qa", "creative"]


def sample_task_type():
    return random.choice(TASK_TYPES)


def query_arm(arm: str, task_type: str):
    """Simulate calling a model. Returns (correct: bool, token_cost, latency_ms)."""
    p = ACCURACY[arm][task_type]
    correct = random.random() < p
    return correct, TOKEN_COST[arm], LATENCY_MS[arm]
