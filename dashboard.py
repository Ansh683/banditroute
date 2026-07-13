"""
Static dashboard: reads log.csv, produces the key plots that make the
"it's learning" story visible at a glance.
"""

import csv
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
import numpy as np

LOG_PATH = "log.csv"

rows = []
with open(LOG_PATH) as f:
    for r in csv.DictReader(f):
        r["step"] = int(r["step"])
        r["correct"] = int(r["correct"])
        r["token_cost"] = float(r["token_cost"])
        r["reward"] = float(r["reward"])
        rows.append(r)

arms = sorted(set(r["arm"] for r in rows))
task_types = sorted(set(r["task_type"] for r in rows))

fig, axes = plt.subplots(2, 2, figsize=(13, 9))
fig.suptitle("BanditRoute — Thompson Sampling Router Learning Curve", fontsize=14, fontweight="bold")

# 1. Arm selection frequency over time (rolling window), overall
ax = axes[0, 0]
window = 100
counts_over_time = {a: [] for a in arms}
for i in range(window, len(rows), 20):
    chunk = rows[i-window:i]
    c = Counter(r["arm"] for r in chunk)
    for a in arms:
        counts_over_time[a].append(c.get(a, 0) / window)
xs = list(range(window, len(rows), 20))
for a in arms:
    ax.plot(xs, counts_over_time[a], label=a)
ax.set_title("Arm Selection Frequency (rolling 100-query window)")
ax.set_xlabel("Query #")
ax.set_ylabel("Selection rate")
ax.legend(fontsize=8)

# 2. Reward over time (rolling average)
ax = axes[0, 1]
rewards = [r["reward"] for r in rows]
roll = np.convolve(rewards, np.ones(window)/window, mode="valid")
ax.plot(roll, color="darkgreen")
ax.set_title("Reward Over Time (rolling avg)")
ax.set_xlabel("Query #")
ax.set_ylabel("Avg reward")

# 3. Final routing preference by task type (last 500 queries = converged behavior)
ax = axes[1, 0]
converged = rows[-500:]
data = defaultdict(lambda: defaultdict(int))
for r in converged:
    data[r["task_type"]][r["arm"]] += 1
x = np.arange(len(task_types))
width = 0.2
for i, a in enumerate(arms):
    vals = [data[t][a] for t in task_types]
    ax.bar(x + i*width, vals, width, label=a)
ax.set_xticks(x + width*1.5)
ax.set_xticklabels(task_types)
ax.set_title("Converged Routing Choice by Task Type (last 500 queries)")
ax.set_ylabel("Times selected")
ax.legend(fontsize=8)

# 4. Cumulative cost saved vs always-large baseline
ax = axes[1, 1]
large_cost_per_query = 0.09
actual_cum = np.cumsum([r["token_cost"] for r in rows])
baseline_cum = np.array([large_cost_per_query * (i+1) for i in range(len(rows))])
ax.plot(baseline_cum, label="Always Fireworks Large", linestyle="--", color="gray")
ax.plot(actual_cum, label="BanditRoute", color="crimson")
ax.set_title("Cumulative Token Cost: Router vs Always-Large Baseline")
ax.set_xlabel("Query #")
ax.set_ylabel("Cumulative $ cost")
ax.legend(fontsize=8)

plt.tight_layout()
plt.savefig("dashboard.png", dpi=130)
print("Saved dashboard.png")
