"""
Reward = Accuracy - lambda * TokenCost - mu * Latency

Raw reward is scaled to roughly [0, 1] so it can double as the
Beta-distribution success signal in the Thompson Sampling update.
"""

LAMBDA = 3.0       # weight on token cost
MU = 0.00003        # weight on latency (ms) — tuned for REAL API latencies (1000-5000ms),
                    # not mock local latencies (180-900ms). Was 0.0006, which zeroed out
                    # every correct-but-slow real response.

CORRECT_BONUS = 1.0
WRONG_PENALTY = -0.3   # not as harsh as -1, else Beta update degenerates fast


def compute_reward(correct: bool, token_cost: float, latency_ms: float) -> float:
    base = CORRECT_BONUS if correct else WRONG_PENALTY
    raw = base - LAMBDA * token_cost - MU * latency_ms
    # squash into [0,1] for the Beta update (simple clip+shift, not true sigmoid —
    # keeps it interpretable for a demo)
    scaled = (raw + 0.3) / 1.3
    return max(0.0, min(1.0, scaled))
