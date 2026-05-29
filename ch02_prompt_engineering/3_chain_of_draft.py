from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

# Standard CoT (verbose — more output tokens)
COT_PROMPT = """Analyse this financial statement. Think through each section carefully,
explaining your reasoning at each step, before giving your final assessment.

Revenue: €2.4M (+18% YoY), Gross Margin: 71%, EBITDA: -€320K, Cash runway: 8 months."""

# Chain-of-Draft (compact — ~75% fewer reasoning tokens, similar accuracy)
COD_PROMPT = """Analyse this financial statement.

Think step by step, but keep each step to one short phrase (5 words max).
Format:
Step 1: [short phrase]
Step 2: [short phrase]
...
Final answer: [full response]

Revenue: €2.4M (+18% YoY), Gross Margin: 71%, EBITDA: -€320K, Cash runway: 8 months."""

if __name__ == "__main__":
    print("=== Standard CoT ===")
    r1 = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1024,
        messages=[{"role": "user", "content": COT_PROMPT}]
    )
    print(r1.content[0].text)
    print(f"\nTokens: {r1.usage.output_tokens}")

    print("\n=== Chain-of-Draft ===")
    r2 = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=512,
        messages=[{"role": "user", "content": COD_PROMPT}]
    )
    print(r2.content[0].text)
    print(f"\nTokens: {r2.usage.output_tokens}")
