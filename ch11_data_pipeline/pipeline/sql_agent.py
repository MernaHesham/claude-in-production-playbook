import sqlite3
import json
import os
from dotenv import load_dotenv
from .base import BaseAgent, Artefact

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sales.db")


class SQLAgent(BaseAgent):
    system = """You are a SQL expert. The database has three tables:
- sales(id, date TEXT, product TEXT, revenue REAL, units INTEGER, customer_id INTEGER, region TEXT)
- products(id, name TEXT, category TEXT, cost_price REAL)
- customers(id, name TEXT, region TEXT, since_date TEXT)

Write SELECT queries only. When you have the data you need, respond with the raw JSON array and nothing else."""

    tools = [{
        "name": "run_sql",
        "description": "Execute a read-only SELECT query against the sales database.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "SELECT statement only."}
            },
            "required": ["query"]
        }
    }]

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path

    def _dispatch_tool(self, name, inputs):
        q = inputs["query"].strip()
        if not q.upper().startswith("SELECT"):
            return "Error: only SELECT queries are permitted."
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(q).fetchall()
            return json.dumps([dict(r) for r in rows])

    def _parse(self, text) -> Artefact:
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = text
        return Artefact(kind="data", content=data)
