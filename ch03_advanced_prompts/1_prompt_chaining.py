from dotenv import load_dotenv
from typing import Optional
import anthropic

load_dotenv()
client = anthropic.Anthropic()


def chain_call(
    prompt: str,
    system: Optional[str] = None,
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 2048
) -> str:
    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}]
    }
    if system:
        kwargs["system"] = system
    response = client.messages.create(**kwargs)
    return response.content[0].text


def analyse_earnings_report(raw_text: str) -> dict:
    """Three-step chain: extract → analyse → simplify."""
    extracted = chain_call(
        prompt=f"""Extract the following from this earnings report as JSON:
revenue_q, gross_margin_pct, ebitda, guidance_raised (bool), key_risks (list)

<report>{raw_text}</report>

Return only valid JSON, no prose."""
    )

    analysis = chain_call(
        prompt=f"""You are a buy-side equity analyst. Analyse this structured earnings data:

{extracted}

Provide: (1) one-sentence verdict, (2) top 3 risks, (3) top 2 opportunities.
Be specific — cite the numbers."""
    )

    summary = chain_call(
        prompt=f"""Translate this analyst report into plain English for a retail investor.
No jargon. Max 150 words. Use simple bullet points.

{analysis}"""
    )

    return {"raw_extract": extracted, "analyst_view": analysis, "plain_summary": summary}


if __name__ == "__main__":
    sample = """Q3 2025 Results: Revenue $142M (+23% YoY), Gross margin 68%, EBITDA $12M.
    Guidance raised to $580-590M for full year. Key risks: customer concentration (top 3 = 41% revenue),
    FX headwinds, increased sales cycle length in enterprise."""
    result = analyse_earnings_report(sample)
    print("=== Plain Summary ===")
    print(result["plain_summary"])
