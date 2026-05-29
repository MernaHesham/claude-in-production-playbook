from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

if __name__ == "__main__":
    # Count tokens BEFORE sending — useful for cost estimation and context management
    messages = [
        {"role": "user", "content": "Explain the difference between RAG and fine-tuning for production AI."}
    ]

    count = client.messages.count_tokens(
        model="claude-sonnet-4-6",
        system="You are a helpful AI engineer. Keep answers concise.",
        messages=messages
    )
    print(f"This request will use {count.input_tokens} input tokens")
    print(f"Estimated input cost: ${count.input_tokens * 3 / 1_000_000:.6f} (Sonnet rate)")

    # Now actually send it
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system="You are a helpful AI engineer. Keep answers concise.",
        messages=messages
    )
    print(f"\nActual input tokens:  {response.usage.input_tokens}")
    print(f"Actual output tokens: {response.usage.output_tokens}")
    print(f"\nResponse:\n{response.content[0].text}")
