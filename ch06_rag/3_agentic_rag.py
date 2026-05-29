from dotenv import load_dotenv
import json
import chromadb
import anthropic
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

load_dotenv()
client = anthropic.Anthropic()
chroma = chromadb.Client()
embedder = SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")
collection = chroma.get_or_create_collection("knowledge_base", embedding_function=embedder)

rag_tool = {
    "name": "search_knowledge_base",
    "description": (
        "Search the knowledge base for relevant information. "
        "Call this multiple times with different queries if needed. "
        "Returns the top relevant text chunks."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "A specific, targeted search query (not the full user question)"
            },
            "n_results": {
                "type": "integer",
                "description": "Number of results (2-8)",
                "default": 4
            }
        },
        "required": ["query"]
    }
}


def execute_rag_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "search_knowledge_base":
        results = collection.query(
            query_texts=[tool_input["query"]],
            n_results=tool_input.get("n_results", 4)
        )
        return json.dumps({
            "results": results["documents"][0],
            "count": len(results["documents"][0])
        })
    raise ValueError(f"Unknown tool: {tool_name}")


def run_agentic_rag(user_message: str) -> str:
    """Agentic RAG — Claude decides how many searches to run."""
    messages = [{"role": "user", "content": user_message}]
    for _ in range(10):
        response = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=2048,
            tools=[rag_tool], messages=messages
        )
        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if b.type == "text")
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_rag_tool(block.name, block.input)
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
        messages.append({"role": "user", "content": tool_results})
    return "Max iterations reached."


if __name__ == "__main__":
    import os
    kb_path = os.path.join(os.path.dirname(__file__), "..", "data", "knowledge_base.txt")
    text = open(kb_path).read()
    # Quick ingest for demo
    chunks = [text[i:i+800] for i in range(0, len(text), 640)]
    collection.add(
        documents=chunks,
        ids=[f"kb-{i}" for i in range(len(chunks))],
        metadatas=[{"source": "knowledge_base"}] * len(chunks)
    )
    answer = run_agentic_rag("What is the refund policy for enterprise contracts, and how does it differ from monthly plans?")
    print(answer)
