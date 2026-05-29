"""
Rate limiting — Chapter 14.

Sliding-window rate limiter backed by Redis.
Default: 20 requests per user per 60-second window.

Why rate limit Claude applications specifically:
  - Anthropic charges per token — a runaway user can spike your bill instantly
  - LLM responses are slow; concurrency limits prevent queue starvation
  - Abuse vectors (prompt injection, jailbreak attempts) often come in bursts

Run Redis locally for testing:
  docker run -p 6379:6379 redis:7-alpine

Install: pip install redis
"""

import time
import redis
import anthropic
from dotenv import load_dotenv

load_dotenv()

r = redis.Redis(host="localhost", port=6379, decode_responses=True)
client = anthropic.Anthropic()


def check_rate_limit(user_id: str, limit: int = 20, window: int = 60) -> bool:
    """
    Sliding fixed-window rate limiter.
    Returns True if the request is allowed, False if the limit is exceeded.
    Key rotates every `window` seconds so the window always resets cleanly.
    """
    key = f"rl:{user_id}:{int(time.time()) // window}"
    current = r.incr(key)
    if current == 1:
        r.expire(key, window * 2)  # TTL = 2× window so we don't lose the count mid-window
    return current <= limit


def remaining(user_id: str, limit: int = 20, window: int = 60) -> int:
    """How many requests this user has left in the current window."""
    key = f"rl:{user_id}:{int(time.time()) // window}"
    used = int(r.get(key) or 0)
    return max(0, limit - used)


def ask(user_id: str, question: str) -> str:
    """Rate-checked Claude call. Raises RuntimeError if limit exceeded."""
    if not check_rate_limit(user_id):
        raise RuntimeError(
            f"Rate limit exceeded for user {user_id}. "
            f"Try again in {60 - (int(time.time()) % 60)}s."
        )
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text


if __name__ == "__main__":
    try:
        r.ping()
    except redis.ConnectionError:
        print("Redis not running. Start it with: docker run -p 6379:6379 redis:7-alpine")
        raise SystemExit(1)

    user = "user_demo_123"

    # Normal usage
    for i in range(3):
        print(f"Request {i + 1} | remaining={remaining(user)}")
        answer = ask(user, "What is 2 + 2?")
        print(f"  → {answer.strip()}\n")

    # Simulate hitting the limit (set a tiny limit for demo)
    demo_user = "user_burst_test"
    LIMIT = 3
    for i in range(5):
        allowed = check_rate_limit(demo_user, limit=LIMIT)
        status = "ALLOWED" if allowed else "BLOCKED"
        print(f"Burst request {i + 1}: {status} (remaining={remaining(demo_user, limit=LIMIT)})")
