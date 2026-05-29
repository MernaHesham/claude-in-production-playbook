from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mangum import Mangum

load_dotenv()

try:
    from agent.orchestrator import research
except ImportError:
    async def research(q): return {"answer": "orchestrator not found", "sources": []}

app = FastAPI(title="Research Assistant")


class Query(BaseModel):
    question: str


@app.post("/research")
async def run_research(q: Query):
    if not q.question.strip():
        raise HTTPException(400, "question must not be empty")
    return await research(q.question)


@app.get("/health")
def health():
    return {"status": "ok"}


handler = Mangum(app, lifespan="off")  # ASGI → Lambda
