from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

if __name__ == "__main__":
    # Adaptive thinking: Claude decides whether and how much to think
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        messages=[{
            "role": "user",
            "content": "What is 2 + 2?"  # Simple — Claude will skip thinking
        }]
    )
    print("Simple question:")
    for block in response.content:
        if block.type == "thinking":
            print(f"  Thinking: {len(block.thinking)} chars")
        elif block.type == "text":
            print(f"  Answer: {block.text}")

    response2 = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        messages=[{
            "role": "user",
            "content": "We are a 4-person B2B SaaS startup, 6 months from launch. Should we use microservices or a monolith? Consider ops capacity, failure modes, and team size."
        }]
    )
    print("\nComplex question:")
    for block in response2.content:
        if block.type == "thinking":
            print(f"  Thinking: {len(block.thinking)} chars")
        elif block.type == "text":
            print(f"  Answer: {block.text[:300]}...")
