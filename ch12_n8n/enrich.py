from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import anthropic
import httpx
import json

load_dotenv()

app = FastAPI()
client = anthropic.Anthropic()


class Lead(BaseModel):
    company_name: str
    website: str
    contact_title: str


ENRICH = """Enrich CRM leads. Return JSON:
{"icp_score":1-10,"icp_reason":"one sentence",
 "talking_points":["max 3 personalised bullets"],
 "recommended_sequence":"cold_email|warm_call|demo_request",
 "estimated_deal_size":"S(<10k)|M(10-50k)|L(50k+)"}"""


@app.post("/enrich")
async def enrich(lead: Lead):
    try:
        async with httpx.AsyncClient(timeout=10) as h:
            ctx = (await h.get(lead.website)).text[:3000]
    except Exception:
        ctx = "(website unavailable)"
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=512, system=ENRICH,
        messages=[{"role": "user", "content": f"{lead.company_name} — {lead.contact_title}\n{ctx}"}],
    )
    return json.loads(resp.content[0].text)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
