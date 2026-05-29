import json
from dotenv import load_dotenv
import anthropic
from .sql_agent import SQLAgent
from .viz_agent import VizAgent
from .base import Artefact, client

load_dotenv()

sql = SQLAgent()
viz = VizAgent()

SYSTEM = """You orchestrate a data analysis pipeline. You have two agents:
- sql_agent: queries the sales database with natural language
- viz_agent: creates charts from tabular data

Always query data first, then optionally create a chart, then write the final Markdown report yourself."""

tools = [
    {
        "name": "sql_agent",
        "description": "Query the sales database with a natural language question.",
        "input_schema": {
            "type": "object",
            "properties": {"question": {"type": "string"}},
            "required": ["question"]
        }
    },
    {
        "name": "viz_agent",
        "description": "Create a chart. Pass the data array and a descriptive chart title.",
        "input_schema": {
            "type": "object",
            "properties": {
                "data": {"type": "array"},
                "chart_title": {"type": "string"}
            },
            "required": ["data", "chart_title"]
        }
    },
]


def analyse(question: str) -> dict:
    messages = [{"role": "user", "content": question}]
    artefacts = []

    while True:
        resp = client.messages.create(
            model="claude-opus-4-7", max_tokens=4096,
            system=SYSTEM, tools=tools, messages=messages
        )
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason == "end_turn":
            report = next(b.text for b in resp.content if b.type == "text")
            return {"report": report, "artefacts": artefacts}

        results = []
        for b in resp.content:
            if b.type != "tool_use":
                continue
            if b.name == "sql_agent":
                art = sql.run(b.input["question"])
            else:
                data_art = Artefact("data", b.input["data"])
                art = viz.run(b.input.get("chart_title", "Chart"), context=[data_art])
            artefacts.append(art)
            results.append({
                "type": "tool_result",
                "tool_use_id": b.id,
                "content": str(art.content)
            })
        messages.append({"role": "user", "content": results})
