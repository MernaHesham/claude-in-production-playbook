import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# The 10 most common Claude prompt failures — each shown as bad vs fixed.
#
# 1  Vague output format          → specify structure with <output_format>
# 2  Missing audience context     → add <audience> tag to system prompt
# 3  Constraints buried mid-para  → move critical constraints to a list
# 4  Not giving Claude permission to ask → "If unclear, ask before proceeding."
# 5  Under-specifying length       → "around 200 words", not "concise"
# 6  Conflating task and context   → separate with <task> and <context> tags
# 7  No examples for custom format → add 2-3 few-shot examples
# 8  Asking for JSON with no schema → define the schema explicitly
# 9  Multi-step tasks in one call  → use prompt chaining (Chapter 3)
# 10 Relying on defaults for tone  → explicit persona always beats defaults


def failure_1_vague_format(text: str) -> str:
    """Bad: 'write a report'. Fixed: explicit <output_format> block."""
    prompt = f"""<task>Summarise the following customer feedback.</task>

<context>{text}</context>

<output_format>
## Summary (2 sentences max)
## Top 3 Issues (bullet list)
## Recommended Action (1 sentence)
</output_format>"""
    r = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    return r.content[0].text


def failure_8_json_no_schema(text: str) -> str:
    """Bad: 'return JSON'. Fixed: schema defined in prompt."""
    prompt = f"""Extract the key details from the support ticket below.
Return valid JSON matching this exact schema:

{{
  "category": "billing | technical | account | other",
  "priority": "low | medium | high",
  "summary": "string (max 20 words)",
  "requires_human": true | false
}}

Ticket:
{text}"""
    r = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )
    return r.content[0].text


def failure_4_no_permission_to_ask(task: str) -> str:
    """Fixed: explicitly grant Claude permission to ask clarifying questions."""
    prompt = f"""{task}

If anything is unclear or if you need additional context to complete this well,
ask your questions before proceeding. Do not guess at ambiguous requirements."""
    r = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    return r.content[0].text


if __name__ == "__main__":
    sample_feedback = (
        "The dashboard takes forever to load and half the charts are broken. "
        "Also I was double-charged last month and nobody replied to my support email."
    )

    print("=== Failure 1 fix — structured output format ===")
    print(failure_1_vague_format(sample_feedback))

    print("\n=== Failure 8 fix — JSON with schema ===")
    print(failure_8_json_no_schema(sample_feedback))

    print("\n=== Failure 4 fix — permission to ask ===")
    vague_task = "Write a blog post about our new product launch."
    print(failure_4_no_permission_to_ask(vague_task))
