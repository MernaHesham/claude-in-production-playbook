import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

# Connect Claude to a running MCP server using the Anthropic API's MCP Connector.
# Claude automatically discovers the server's available tools and uses them during inference.
# Run server.py first, then run this script.
#
# MCP vs Direct Tool Calling:
#   Direct tool use  → define JSON schema inline, tool runs in-process, per-app
#   MCP server       → separate process, any MCP client can connect, share across team
#   Use direct tool calling for prototypes; MCP for shared production connectors.
#
# Security note: MCP provides no authentication by default.
# Validate all inputs and apply minimum-privilege principles to the server process.


def query_via_mcp(question: str) -> str:
    """Send a question to Claude; Claude uses MCP tools to answer it."""
    with client.beta.mcp.sessions.stdio_session(
        command=["python", "server.py"]
    ) as session:
        response = client.beta.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            mcp_servers=[session],
            messages=[{"role": "user", "content": question}]
        )
        return response.content[0].text


if __name__ == "__main__":
    questions = [
        "What tables exist in our database? Show me the first 5 rows of the revenue table.",
        "Summarise the top 3 revenue entries.",
    ]
    for q in questions:
        print(f"Q: {q}")
        print(f"A: {query_via_mcp(q)}")
        print()
