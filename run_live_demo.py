"""
Live demo: runs the SAME contextual Thompson Sampling bandit from bandit.py,
but against real OpenRouter API calls instead of mock arms.

Respects free-tier rate limits (20 req/min) by pacing requests.
Designed to run ~40 real queries — well under the 50/day free cap.
"""

import csv
import time
import random
from bandit import ThompsonRouter
from reward import compute_reward
from real_models import REAL_ARMS, TOKEN_COST, call_model
from eval_queries import EVAL_QUERIES

N_ROUNDS = 2          # each round = 1 pass through the ~20 eval queries' task types
PACING_SECONDS = 5.0  # popular free models (e.g. qwen3-coder) can be rate-limited
                       # via a shared pool faster than the per-account cap suggests
LOG_PATH = "live_log.csv"


def grade(response_text: str, keywords):
    if not keywords:
        # creative / open-ended — "correct" if it produced a real, non-trivial answer
        return len(response_text.strip()) > 5
    text_lower = response_text.lower()
    return any(kw.lower() in text_lower for kw in keywords)


def main():
    router = ThompsonRouter()
    # seed the bandit's arm set to match REAL_ARMS (bandit.py imports ARMS from
    # models.py by default — for the live demo we override at call time)
    for t in router.alpha:
        router.alpha[t] = {a: 1.0 for a in REAL_ARMS}
        router.beta[t] = {a: 1.0 for a in REAL_ARMS}

    rows = []
    query_pool = EVAL_QUERIES * N_ROUNDS
    random.shuffle(query_pool)

    for i, (task_type, prompt, keywords) in enumerate(query_pool):
        # select_arm uses router.alpha[task_type] keys as the arm set
        samples = {a: random.betavariate(router.alpha[task_type][a], router.beta[task_type][a])
                   for a in REAL_ARMS}
        arm = max(samples, key=samples.get)

        print(f"[{i+1}/{len(query_pool)}] task={task_type} -> arm={arm} ... ", end="", flush=True)
        try:
            response_text, latency_ms = call_model(arm, prompt)
        except Exception as e:
            print(f"FAILED ({e})")
            if "Rate limited" in str(e):
                print("  backing off 20s before continuing...")
                time.sleep(20)
            else:
                time.sleep(PACING_SECONDS)
            continue

        correct = grade(response_text, keywords)
        reward = compute_reward(correct, TOKEN_COST[arm], latency_ms)

        r = max(0.0, min(1.0, reward))
        router.alpha[task_type][arm] += r
        router.beta[task_type][arm] += (1 - r)

        print(f"correct={correct} latency={latency_ms:.0f}ms reward={reward:.2f}")

        rows.append({
            "step": i, "task_type": task_type, "arm": arm,
            "correct": int(correct), "token_cost": TOKEN_COST[arm],
            "latency_ms": latency_ms, "reward": reward,
            "response_snippet": response_text[:80].replace("\n", " "),
        })

        time.sleep(PACING_SECONDS)

    if rows:
        with open(LOG_PATH, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        acc = sum(r["correct"] for r in rows) / len(rows)
        print(f"\nDone. {len(rows)} real queries. Overall accuracy: {acc*100:.1f}%")
        print(f"Log written to {LOG_PATH}")
    else:
        print("No successful queries — check your API key and rate limits.")


if __name__ == "__main__":
    main()
