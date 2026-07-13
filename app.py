"""
BanditRoute — interactive Streamlit demo.

Runs the same Thompson Sampling bandit as run_simulation.py, but lets
the viewer control query count and watch routing converge live, with
charts instead of a static PNG.
"""

import random
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from collections import Counter, defaultdict

from models import query_arm, sample_task_type, ARMS, TOKEN_COST, TASK_TYPES
from bandit import ThompsonRouter
from reward import compute_reward

st.set_page_config(page_title="BanditRoute", layout="wide", page_icon="🎰")

st.title("🎰 BanditRoute")
st.caption("A reinforcement-learning router that learns which AI model to call — instead of hardcoding a rule.")

with st.sidebar:
    st.header("Simulation controls")
    n_queries = st.slider("Number of queries", 200, 5000, 2000, step=100)
    seed = st.number_input("Random seed", value=42, step=1)
    run_button = st.button("Run simulation", type="primary", use_container_width=True)

    st.divider()
    st.markdown("**How it works**")
    st.markdown(
        "- 4 models = 4 bandit arms, each with a different accuracy/cost/latency profile per task type\n"
        "- Thompson Sampling picks an arm per query, conditioned on task type\n"
        "- `reward = accuracy − λ·cost − μ·latency`\n"
        "- No routing rule was hand-written — it all comes from reward feedback"
    )
    st.divider()
    st.caption("Also validated against real free-tier models via the OpenRouter API — see `run_live_demo.py` in the repo.")


def run_simulation(n, seed):
    random.seed(seed)
    router = ThompsonRouter()
    rows = []
    for i in range(n):
        task_type = sample_task_type()
        arm = router.select_arm(task_type)
        correct, token_cost, latency_ms = query_arm(arm, task_type)
        reward = compute_reward(correct, token_cost, latency_ms)
        router.update(task_type, arm, reward)
        rows.append({
            "step": i, "task_type": task_type, "arm": arm,
            "correct": int(correct), "token_cost": token_cost,
            "latency_ms": latency_ms, "reward": reward,
        })
    return rows


if run_button or "rows" not in st.session_state:
    with st.spinner("Running simulation..."):
        st.session_state["rows"] = run_simulation(n_queries, seed)

rows = st.session_state["rows"]
n = len(rows)

# ---- top stats ----
total_correct = sum(r["correct"] for r in rows)
total_cost = sum(r["token_cost"] for r in rows)
always_large_cost = n * TOKEN_COST["fireworks_large"]
saved_pct = 100 * (1 - total_cost / always_large_cost) if always_large_cost > 0 else 0

c1, c2, c3 = st.columns(3)
c1.metric("Overall accuracy", f"{100*total_correct/n:.1f}%")
c2.metric("Cost saved vs. always-large", f"{saved_pct:.1f}%")
c3.metric("Queries simulated", f"{n:,}")

st.divider()

arms = sorted(set(r["arm"] for r in rows))
task_types = sorted(set(r["task_type"] for r in rows))

# ---- arm selection frequency over time ----
col1, col2 = st.columns(2)

with col1:
    st.subheader("Arm selection over time")
    window = max(20, n // 40)
    fig, ax = plt.subplots(figsize=(6, 4))
    xs = list(range(window, n, max(1, n // 100)))
    for a in arms:
        ys = []
        for i in xs:
            chunk = rows[i - window:i]
            c = Counter(r["arm"] for r in chunk)
            ys.append(c.get(a, 0) / window)
        ax.plot(xs, ys, label=a)
    ax.set_xlabel("Query #")
    ax.set_ylabel("Selection rate")
    ax.legend(fontsize=8)
    st.pyplot(fig)

with col2:
    st.subheader("Reward over time")
    fig, ax = plt.subplots(figsize=(6, 4))
    rewards = [r["reward"] for r in rows]
    w = max(10, n // 40)
    roll = np.convolve(rewards, np.ones(w) / w, mode="valid")
    ax.plot(roll, color="darkgreen")
    ax.set_xlabel("Query #")
    ax.set_ylabel("Avg reward (rolling)")
    st.pyplot(fig)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Converged routing by task type")
    converged = rows[-max(50, n // 4):]
    data = defaultdict(lambda: defaultdict(int))
    for r in converged:
        data[r["task_type"]][r["arm"]] += 1
    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.arange(len(task_types))
    width = 0.8 / len(arms)
    for i, a in enumerate(arms):
        vals = [data[t][a] for t in task_types]
        ax.bar(x + i * width, vals, width, label=a)
    ax.set_xticks(x + width * (len(arms) - 1) / 2)
    ax.set_xticklabels(task_types)
    ax.legend(fontsize=8)
    st.pyplot(fig)

with col4:
    st.subheader("Cumulative cost: router vs always-large")
    fig, ax = plt.subplots(figsize=(6, 4))
    large_cost = TOKEN_COST["fireworks_large"]
    actual_cum = np.cumsum([r["token_cost"] for r in rows])
    baseline_cum = np.array([large_cost * (i + 1) for i in range(n)])
    ax.plot(baseline_cum, "--", color="gray", label="Always Fireworks Large")
    ax.plot(actual_cum, color="crimson", label="BanditRoute")
    ax.set_xlabel("Query #")
    ax.set_ylabel("Cumulative $ cost")
    ax.legend(fontsize=8)
    st.pyplot(fig)

st.divider()
st.caption("Simulated arms: mock accuracy/cost/latency profiles per task type — see `models.py`. Live OpenRouter integration also included in the repo (`real_models.py`, `run_live_demo.py`).")
