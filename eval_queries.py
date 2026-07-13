"""
Small hand-labeled eval set so we can score REAL model responses against
a known-correct answer (simple substring/keyword match — not a full
grading LLM, but enough for a live demo to show accuracy differences).
"""

EVAL_QUERIES = [
    # task_type, prompt, answer_keywords (any one match = correct)
    ("math", "What is 17 * 24? Answer with just the number.", ["408"]),
    ("math", "What is the square root of 144? Just the number.", ["12"]),
    ("math", "If a train travels 60 mph for 2.5 hours, how far does it go? Just the number in miles.", ["150"]),
    ("math", "What is 15% of 200? Just the number.", ["30"]),
    ("math", "Solve for x: 2x + 6 = 20. Just the number.", ["7"]),

    ("code", "Write a Python one-liner to reverse a string called s.", ["s[::-1]", "reversed(s)"]),
    ("code", "In Python, what function converts a string to an integer?", ["int("]),
    ("code", "What Python keyword defines a function?", ["def"]),
    ("code", "What does len([1,2,3]) return in Python? Just the number.", ["3"]),
    ("code", "What symbol is used for a comment in Python?", ["#"]),

    ("qa", "What is the capital of France?", ["paris"]),
    ("qa", "What is the largest planet in our solar system?", ["jupiter"]),
    ("qa", "How many continents are there?", ["7", "seven"]),
    ("qa", "What is the chemical symbol for water?", ["h2o", "h₂o"]),
    ("qa", "Who wrote Romeo and Juliet?", ["shakespeare"]),

    ("creative", "Write one short sentence describing autumn leaves.", []),  # graded as always-plausible
    ("creative", "Give a one-line metaphor for the ocean.", []),
    ("creative", "Write a two-word title for a story about a lost dog.", []),
    ("creative", "Describe the color blue in one sentence.", []),
    ("creative", "Give one creative name for a coffee shop.", []),
]
