from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

if __name__ == "__main__":
    hard_problem = (
        "A company has 3 warehouses (A, B, C) and 4 stores (1, 2, 3, 4). "
        "Shipping costs per unit: A→1=2, A→2=3, A→3=1, A→4=5, "
        "B→1=4, B→2=1, B→3=2, B→4=3, C→1=3, C→2=5, C→3=4, C→4=2. "
        "Supply: A=100, B=80, C=120. Demand: 1=70, 2=90, 3=80, 4=60. "
        "Find the shipping plan that minimises total cost."
    )

    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16000,
        thinking={"type": "enabled", "budget_tokens": 10000},
        messages=[{"role": "user", "content": hard_problem}],
    )

    for block in response.content:
        if block.type == "thinking":
            print(f"[Reasoning — {len(block.thinking)} chars]")
            print(block.thinking[:400], "...\n")
        elif block.type == "text":
            print("[Answer]")
            print(block.text)
