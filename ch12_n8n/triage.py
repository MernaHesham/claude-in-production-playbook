from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
import anthropic
import json

load_dotenv()

app = FastAPI()
client = anthropic.Anthropic()


class Ticket(BaseModel):
    subject: str
    body: str
    from_email: str


SYSTEM = """Classify support tickets. Return ONLY valid JSON:
{"priority":"critical|high|medium|low","category":"billing|technical|feature|general",
 "sentiment":"frustrated|neutral|positive","suggested_team":"engineering|billing|sales|support",
 "draft_response":"2-3 sentence empathetic acknowledgement",
 "internal_note":"one sentence for the agent"}"""


@app.post("/triage")
def triage(t: Ticket):
    resp = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=512, system=SYSTEM,
        messages=[{"role": "user", "content": f"From: {t.from_email}\nSubject: {t.subject}\n\n{t.body}"}],
    )
    return json.loads(resp.content[0].text)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
