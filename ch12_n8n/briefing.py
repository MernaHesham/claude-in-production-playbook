from dotenv import load_dotenv
from fastapi import FastAPI
import anthropic

load_dotenv()

app = FastAPI()
client = anthropic.Anthropic()

BRIEFING = """Write a founder briefing from the past 24 hours of AI news.
Format (Markdown, max 400 words):
## Research — 2-3 bullets on papers or model releases
## Industry — 2-3 bullets on funding, acquisitions, partnerships
## What This Means For Us — 1-2 bullets relevant to a Claude-based SaaS
Be opinionated, not neutral."""


@app.post("/briefing")
def briefing(headlines: list[str]):
    resp = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=800, system=BRIEFING,
        messages=[{"role": "user", "content": "\n".join(f"- {h}" for h in headlines)}],
    )
    return {"briefing": resp.content[0].text}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
