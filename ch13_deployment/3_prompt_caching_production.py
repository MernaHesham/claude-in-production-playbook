"""
Prompt caching in production — Chapter 13.

Economics:
  Cache writes: 25% more than normal input tokens
  Cache reads:  10% of normal input tokens
  Break-even:   2 reads

At 1,000 calls with a 50K-token context on Sonnet, caching saves ~$112.
Any system prompt used more than twice should use caching.

Rules:
  - The cached content must be identical between calls (any change invalidates it)
  - Only the messages list (user turn) can vary freely
  - Cache TTL is 1 hour
  - Minimum cacheable prefix: 1,024 tokens (~750 words)
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

KNOWLEDGE_BASE = open(
    os.path.join(os.path.dirname(__file__), "..", "data", "document.txt")
).read() if os.path.exists(
    os.path.join(os.path.dirname(__file__), "..", "data", "document.txt")
) else "This is a placeholder knowledge base. " * 100  # fallback for demo


def ask_with_cache(question: str) -> tuple[str, int, int]:
    """Query the knowledge base. Returns (answer, cache_read_tokens, cache_write_tokens)."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": KNOWLEDGE_BASE,
                "cache_control": {"type": "ephemeral"},
            },
            {
                "type": "text",
                "text": "Answer using only the knowledge base above. Be concise.",
            },
        ],
        messages=[{"role": "user", "content": question}],
    )
    return (
        response.content[0].text,
        response.usage.cache_read_input_tokens,
        response.usage.cache_creation_input_tokens,
    )


if __name__ == "__main__":
    questions = [
        "What does this document cover?",
        "Summarise the main points in three bullets.",
        "What is the most important takeaway?",
    ]

    for i, q in enumerate(questions, 1):
        answer, cache_read, cache_write = ask_with_cache(q)
        status = "CACHE WRITE (first call)" if cache_write > 0 else "CACHE HIT  (90% cost)"
        print(f"Call {i} [{status}]")
        print(f"  cache_write={cache_write:,}  cache_read={cache_read:,}")
        print(f"  Q: {q}")
        print(f"  A: {answer[:120]}...")
        print()
