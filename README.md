# BanditRoute

A router that learns *which AI model to call* for a given query, instead
of relying on hardcoded rules like `if difficulty > 0.7`.

## The idea

Treat each model as an "arm" in a multi-armed bandit. Use **Thompson
Sampling**, conditioned on task type (code / math / qa / creative), so the
router learns per-category — this is a real, if simple, contextual bandit.
The reward function balances accuracy against token cost and latency, so
the router isn't just optimizing for "get it right" — it's optimizing for
"get it right cheaply and fast."

No routing rule was hand-written. Whatever preferences show up (e.g.
routing math to the strongest model, routing easy QA to a cheap one)
emerged from reward feedback over time.

## What's actually working

The **simulation is solid and fully working end to end**. `run_simulation.py`
runs 2000 queries against 4 mock model "arms" (each with a different
accuracy/cost/latency profile per task type), and the bandit visibly learns
the right model for the right job within a few hundred queries. Results
from the last run:

- 77.5% overall accuracy
- 92.8% cost savings vs. always routing to the most expensive model
- Clear per-task routing preferences emerge within ~300-500 queries

`dashboard.py` turns that into a 4-panel chart showing the learning curve,
converged routing choices per task, and cumulative cost saved.

## What's real but rougher

I also wired up a live version (`real_models.py` + `run_live_demo.py`)
that runs the *exact same bandit* against real, free-tier models on
OpenRouter (Llama 3.3 70B, Qwen3 Coder, GPT-OSS 20B, Llama 3.2 3B) instead
of mock data, graded against a small hand-labeled answer key.

Honestly — this part is a work in progress, not a finished result. Free-tier
model slugs on OpenRouter rotate without much notice (a couple I originally
picked had already been retired), and popular free models get rate-limited
by shared-pool congestion independent of your own usage, so live runs are
slower and less predictable than the simulation. The code is correct and
does make real API calls with real responses — I just didn't get a full
clean 40-query run in the time I had. If you run it yourself with a fresh
API key, it should work, possibly with a retry here or there.

I think that's worth being upfront about rather than dressing it up: the
core RL idea is real and demonstrated cleanly in simulation; the live
integration proves it isn't just theoretical, but it's the part that would
get hardened next, not the finished product.

## Files

- `models.py` — mock arms with per-task accuracy/cost/latency profiles
- `bandit.py` — the contextual Thompson Sampling router (the core logic,
  shared by both simulated and live modes)
- `reward.py` — reward shaping (accuracy − λ·cost − μ·latency)
- `run_simulation.py` — runs 2000 simulated queries → `log.csv`
- `dashboard.py` — `log.csv` → `dashboard.png`
- `real_models.py` — real OpenRouter API client (free-tier models)
- `eval_queries.py` — 20 hand-labeled questions used to grade real responses
- `run_live_demo.py` — runs real queries through the same bandit → `live_log.csv`
- `live_dashboard.py` — `live_log.csv` → `live_dashboard.png`

## Running it

Simulation (no API key needed, works immediately):
```
python3 run_simulation.py
python3 dashboard.py
```

Live demo (needs a free OpenRouter API key, see `real_models.py` for setup):
```
python3 run_live_demo.py
python3 live_dashboard.py
```

## If I had more time

- Harden the live integration — retry logic per arm, fallback to a
  different free model when one is congested, maybe a small local model
  via Ollama as a guaranteed-available arm
- Swap task-type context for real query embeddings + LinUCB, for a more
  genuine contextual bandit instead of the current category-based one
- Wrap it in FastAPI so it's a live service instead of a batch script
