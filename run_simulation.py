"""
Runs the full learning loop:

  sample query -> extract task type -> bandit picks arm ->
  "call" model -> compute reward -> update bandit -> log

Then hands off to dashboard.py to render results.
"""

import csv
from models import query_arm, sample_task_type, ARMS, TOKEN_COST
from bandit import ThompsonRouter
from reward import compute_reward

N_QUERIES = 2000
LOG_PATH = "log.csv"


def main():
    router = ThompsonRouter()
    rows = []

    for i in range(N_QUERIES):
        task_type = sample_task_type()
        arm = router.select_arm(task_type)
        correct, token_cost, latency_ms = query_arm(arm, task_type)
        reward = compute_reward(correct, token_cost, latency_ms)
        router.update(task_type, arm, reward)

        rows.append({
            "step": i,
            "task_type": task_type,
            "arm": arm,
            "correct": int(correct),
            "token_cost": token_cost,
            "latency_ms": latency_ms,
            "reward": reward,
        })

    with open(LOG_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    # quick summary
    total_correct = sum(r["correct"] for r in rows)
    total_cost = sum(r["token_cost"] for r in rows)
    always_large_cost = N_QUERIES * TOKEN_COST["fireworks_large"]
    saved_pct = 100 * (1 - total_cost / always_large_cost)

    print(f"Queries: {N_QUERIES}")
    print(f"Accuracy: {100*total_correct/N_QUERIES:.1f}%")
    print(f"Total cost: ${total_cost:.2f}  (vs always-large: ${always_large_cost:.2f})")
    print(f"Cost saved vs always routing to Fireworks Large: {saved_pct:.1f}%")
    print(f"Log written to {LOG_PATH}")


if __name__ == "__main__":
    main()
