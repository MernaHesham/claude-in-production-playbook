from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

CONSTRAINTS = """
<do_not>
- Do not use bullet points in the executive summary section
- Do not hedge every statement with "it's important to note that"
- Do not repeat the question back before answering
- Do not add a disclaimer unless the content is genuinely legally sensitive
- Do not use em-dashes to simulate complexity — use clear sentences instead
</do_not>
"""

SYSTEM = f"""You are a senior business analyst writing executive summaries.
Write in confident, direct prose. Be specific and cite numbers where available.

{CONSTRAINTS}
"""

if __name__ == "__main__":
    request = """Write a one-paragraph executive summary of this situation:
    Our SaaS product has 2,400 customers, €4.2M ARR, 94% gross retention,
    but our NPS dropped from 52 to 38 this quarter after a UI redesign."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=SYSTEM,
        messages=[{"role": "user", "content": request}]
    )
    print(response.content[0].text)
