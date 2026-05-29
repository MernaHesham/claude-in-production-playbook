import anthropic

from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env


# Generate a synthetic document large enough to trigger caching
paragraph = "This is a paragraph of placeholder text used to test prompt caching. " * 20
large_document = paragraph * 80  # ~1,400 tokens — above the 1,024 minimum

user_question = "Summarise this document in one sentence."

# First call — writes to cache (cache_creation_input_tokens > 0)
r1 = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=256,
    system=[{"type": "text", "text": large_document, "cache_control": {"type": "ephemeral"}}],
    messages=[{"role": "user", "content": user_question}]
)
print("Cache written:", r1.usage.cache_creation_input_tokens)  # e.g. 1412
print("Cache read:   ", r1.usage.cache_read_input_tokens)     # 0 on first call

# Second call — reads from cache (cache_read_input_tokens > 0, cost drops to 10%)
r2 = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=256,
    system=[{"type": "text", "text": large_document, "cache_control": {"type": "ephemeral"}}],
    messages=[{"role": "user", "content": "What is the main topic?"}]
)
print("Cache written:", r2.usage.cache_creation_input_tokens)  # 0 — already cached
print("Cache read:   ", r2.usage.cache_read_input_tokens)     # e.g. 1412 — served from cache
