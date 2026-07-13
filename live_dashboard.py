"""
Same visual story as dashboard.py, but reading live_log.csv (real API
results from run_live_demo.py) instead of the simulated log.csv.
"""

import csv
import matplotlib.pyplot as plt
from collections import defaultdict, Counter

LOG_PATH = "live_log.csv"

rows = []
with open(LOG_PATH) as f:
    for r in csv.DictReader(f):
        r["step"] = int(r["step"])
        r["correct"] = int(r["correct"])
        r["latency_ms"] = float(r["latency_ms"])
        r["reward"] = float(r["reward"])
        rows.append(r)

arms = sorted(set(r["arm"] for r in rows))
task_types = sorted(set(r["task_type"] for r in rows))

fig, axes = plt.subplots(2, 2, figsize=(13, 9))
fig.suptitle("BanditRoute — LIVE Run (real OpenRouter API calls)", fontsize=14, fontweight="bold")

# 1. Arm selection over time (raw, since live runs are short — no rolling window)
ax = axes[0, 0]
for a in arms:
    xs = [r["step"] for r in rows if r["arm"] == a]
    ys = [1] * len(xs)
    ax.scatter(xs, [a] * len(xs), label=a, s=60)
ax.set_title("Arm Selected Per Query (in order)")
ax.set_xlabel("Query #")

# 2. Reward per query + cumulative avg
ax = axes[0, 1]
rewards = [r["reward"] for r in rows]
cum_avg = [sum(rewards[:i+1]) / (i+1) for i in range(len(rewards))]
ax.plot(rewards, "o-", alpha=0.4, label="per-query reward")
ax.plot(cum_avg, color="darkgreen", linewidth=2, label="cumulative avg")
ax.set_title("Reward Per Query (live)")
ax.set_xlabel("Query #")
ax.legend(fontsize=8)

# 3. Accuracy and avg latency by arm
ax = axes[1, 0]
acc_by_arm = {}
lat_by_arm = {}
for a in arms:
    arm_rows = [r for r in rows if r["arm"] == a]
    acc_by_arm[a] = sum(r["correct"] for r in arm_rows) / len(arm_rows) if arm_rows else 0
    lat_by_arm[a] = sum(r["latency_ms"] for r in arm_rows) / len(arm_rows) if arm_rows else 0
x = range(len(arms))
ax.bar(x, [acc_by_arm[a] for a in arms], color="steelblue")
ax.set_xticks(x)
ax.set_xticklabels(arms, rotation=20, ha="right", fontsize=8)
ax.set_title("Accuracy by Model (live)")
ax.set_ylabel("Accuracy")

# 4. Routing choice by task type (raw counts, small sample)
ax = axes[1, 1]
data = defaultdict(lambda: defaultdict(int))
for r in rows:
    data[r["task_type"]][r["arm"]] += 1
import numpy as np
xw = np.arange(len(task_types))
width = 0.8 / max(len(arms), 1)
for i, a in enumerate(arms):
    vals = [data[t][a] for t in task_types]
    ax.bar(xw + i * width, vals, width, label=a)
ax.set_xticks(xw + width * (len(arms) - 1) / 2)
ax.set_xticklabels(task_types)
ax.set_title("Routing Choice by Task Type (live, small sample)")
ax.set_ylabel("Times selected")
ax.legend(fontsize=7)

plt.tight_layout()
plt.savefig("live_dashboard.png", dpi=130)
print("Saved live_dashboard.png")

print("\nPer-arm accuracy / avg latency:")
for a in arms:
    print(f"  {a}: acc={acc_by_arm[a]*100:.0f}%  avg_latency={lat_by_arm[a]:.0f}ms")
