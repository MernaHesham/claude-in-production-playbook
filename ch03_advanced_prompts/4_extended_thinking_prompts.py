import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Extended thinking changes how you write prompts.
# Because Claude reasons before answering, lean into that:
# ask it to consider multiple perspectives, check assumptions, work through edge cases.
# Prompts that work well in standard mode often leave the thinking budget underused
# by being too directive.

WEAK_PROMPT = "Should we use a microservices or monolith architecture for this startup?"

STRONG_PROMPT = """We are a 4-person B2B SaaS startup, 6 months from launch,
with 3 paying pilot customers. We are choosing between microservices and a monolith.

Before answering, think through:
- What assumptions am I making about the team's ops capacity?
- What does the research literature say about microservices failures at early stage?
- What specific characteristics of this situation might make one approach better?
- What would have to be true for my recommendation to be wrong?

Then give a direct recommendation with the 3 most important reasons."""

DO_NOT_CONSTRAINTS = """
<do_not>
- Do not use bullet points in the executive summary section
- Do not hedge every statement with "it's important to note that"
- Do not repeat the question back before answering
- Do not add a disclaimer unless the content is genuinely legally sensitive
- Do not use em-dashes to simulate complexity — use clear sentences instead
</do_not>
"""


def ask_with_extended_thinking(prompt: str, effort: str = "high") -> tuple[str, int]:
    # Claude 4: "adaptive" lets Claude decide when to think.
    # Control depth via output_config effort: "low" | "medium" | "high"
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": effort},
        messages=[{"role": "user", "content": prompt}]
    )
    answer = next(b.text for b in response.content if b.type == "text")
    return answer, response.usage.input_tokens


if __name__ == "__main__":
    print("=== Weak prompt (too directive — under-uses thinking budget) ===")
    answer, tokens_in = ask_with_extended_thinking(WEAK_PROMPT, effort="low")
    print(f"Input tokens: {tokens_in}")
    print(answer)

    print("\n=== Strong prompt (exploits the thinking budget) ===")
    answer, tokens_in = ask_with_extended_thinking(STRONG_PROMPT, effort="high")
    print(f"Input tokens: {tokens_in}")
    print(answer)

    print("\n=== Negative prompting — what NOT to do ===")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=DO_NOT_CONSTRAINTS,
        messages=[{"role": "user", "content": "Write an executive summary of our Q3 results: revenue up 18%, churn down 3%, two enterprise deals closed."}]
    )
    print(response.content[0].text)
