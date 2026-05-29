"""
Streaming FastAPI endpoint.
Key: use AsyncAnthropic (not Anthropic) inside async route handlers.
"""
import asyncio
import anthropic
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
async_client = anthropic.AsyncAnthropic()

async def generate_stream(prompt: str):
    async with async_client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    ) as stream:
        async for text in stream.text_stream:
            yield f"data: {text}\n\n"
            await asyncio.sleep(0)
    yield "data: [DONE]\n\n"

@app.post("/chat/stream")
async def chat_stream(request: dict):
    return StreamingResponse(
        generate_stream(request["prompt"]),
        media_type="text/event-stream"
    )

@app.get("/health")
def health():
    return {"status": "ok"}

'''
Run the server in the terminal and keep it open: uvicorn ch04_api.3_streaming_fastapi:app --reload

Run in another terminal: 
curl -X POST http://127.0.0.1:8000/chat/stream \
   -H "Content-Type: application/json" \
   -d '{"prompt": "Explain RAG in 3 sentences"}' \
   --no-buffer
'''