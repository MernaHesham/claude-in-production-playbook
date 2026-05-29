from dotenv import load_dotenv
import anthropic
import json
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

try:
    from rag.pipeline import ingest, retrieve
except ImportError:
    def ingest(url, text): return 0
    def retrieve(query, k=5): return []

client = anthropic.Anthropic()
MODEL = "claude-sonnet-4-6"

SYSTEM = """You are a research assistant. Protocol:
1. Call web_search to find 3-5 relevant sources.
2. Call fetch_url on each promising URL.
3. Synthesise a precise answer with inline citations [Source N: URL].
Never guess — if information is unavailable, say so."""


async def research(question: str) -> dict:
    server_params = StdioServerParameters(command="python", args=["mcp_server/server.py"])
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            mcp_tools = [
                {"name": t.name, "description": t.description, "input_schema": t.inputSchema}
                for t in tools.tools
            ]
            messages = [{"role": "user", "content": question}]
            fetched_urls = []

            while True:
                resp = client.messages.create(
                    model=MODEL, max_tokens=4096, system=SYSTEM,
                    tools=mcp_tools, messages=messages
                )
                messages.append({"role": "assistant", "content": resp.content})

                if resp.stop_reason == "end_turn":
                    answer = next(b.text for b in resp.content if b.type == "text")
                    return {"answer": answer, "sources": fetched_urls}

                tool_results = []
                for block in resp.content:
                    if block.type != "tool_use":
                        continue
                    result = await session.call_tool(block.name, block.input)
                    raw = result.content[0].text
                    if block.name == "fetch_url":
                        url = block.input["url"]
                        ingest(url, raw)
                        fetched_urls.append(url)
                        raw = json.dumps(retrieve(question))
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": raw
                    })
                messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    result = asyncio.run(research("What is Claude extended thinking?"))
    print(result["answer"])
