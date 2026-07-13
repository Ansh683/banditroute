"""
Real OpenRouter integration — replaces the mock arms in models.py with
actual API calls to free-tier models.

Setup:
  1. Sign up at https://openrouter.ai (no card needed)
  2. Create an API key: https://openrouter.ai/keys
  3. export OPENROUTER_API_KEY="sk-or-..."
  4. pip install requests

Free tier limits (as of mid-2026): 20 requests/min, 50 requests/day
(1000/day if you've ever bought $10+ credit). That's why the live demo
runs ~40 queries, not thousands — see run_live_demo.py.
"""

import os
import time
import requests

# Optional: load from a .env file in the project root, so the key works
# regardless of how the script is launched (terminal, VS Code debugger, etc).
# Create a file named ".env" next to this script containing one line:
#   OPENROUTER_API_KEY=sk-or-your-key-here
def _load_dotenv():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

_load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# 4 real free-tier models standing in for the "arms". Swap slugs any time —
# check current free roster at https://openrouter.ai/models?fmt=free
REAL_ARMS = {
    "llama3_70b":    "meta-llama/llama-3.3-70b-instruct:free",
    "qwen_coder":    "qwen/qwen3-coder:free",
    "gpt_oss_20b":   "openai/gpt-oss-20b:free",
    "llama3_3b":     "meta-llama/llama-3.2-3b-instruct:free",
}

# Rough per-model latency/cost characterization we still track even though
# $ cost is $0 on the free tier — kept so the reward function and dashboard
# still tell a "cost-aware routing" story. Set to 0 since these are free.
TOKEN_COST = {a: 0.0 for a in REAL_ARMS}


def call_model(arm: str, prompt: str, max_tokens: int = 200):
    """Real API call. Returns (response_text, latency_ms)."""
    if not OPENROUTER_API_KEY:
        raise RuntimeError("Set OPENROUTER_API_KEY environment variable first.")

    model_slug = REAL_ARMS[arm]
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model_slug,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }

    start = time.time()
    resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=60)
    latency_ms = (time.time() - start) * 1000

    if resp.status_code == 429:
        raise RuntimeError("Rate limited by OpenRouter free tier — slow down or wait.")
    resp.raise_for_status()

    data = resp.json()
    text = data["choices"][0]["message"]["content"]
    return text, latency_ms
