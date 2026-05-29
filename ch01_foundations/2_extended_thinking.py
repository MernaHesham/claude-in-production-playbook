from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

if __name__ == "__main__":
    # Claude 4: use "adaptive" (Claude decides when/how much to think).
    # Control effort level via output_config: "low" | "medium" | "high"
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": "high"},
        messages=[{
            "role": "user",
            "content": "Design the database schema for a multi-tenant SaaS billing system. Include tables, relationships, and indexes."
        }]
    )

    for block in response.content:
        if block.type == "thinking":
            print(f"[Thinking — {len(block.thinking)} chars]")
            print(block.thinking[:500], "...\n")
        elif block.type == "text":
            print("[Answer]")
            print(block.text)
