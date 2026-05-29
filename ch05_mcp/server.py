import asyncio
import sqlite3
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

app = Server("analytics-server")

DB_PATH = "data/sales.db"


@app.list_tools()
async def list_tools():
    return [
        types.Tool(
            name="list_tables",
            description="List all tables in the analytics database",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="query_table",
            description="Run a read-only SQL SELECT query on the analytics database",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {
                        "type": "string",
                        "description": "SELECT statement only. No mutation queries."
                    }
                },
                "required": ["sql"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    if name == "list_tables":
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row["name"] for row in cursor.fetchall()]
        conn.close()
        return [types.TextContent(type="text", text=", ".join(tables))]

    elif name == "query_table":
        sql = arguments["sql"].strip()
        if not sql.upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed")
        cursor = conn.execute(sql)
        rows = [dict(row) for row in cursor.fetchmany(100)]
        conn.close()
        import json
        return [types.TextContent(type="text", text=json.dumps(rows, indent=2))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
