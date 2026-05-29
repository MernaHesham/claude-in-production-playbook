import datetime
import concurrent.futures
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

# Tools and execute_tool are defined here directly because Python cannot import
# from a module whose filename starts with a digit (4_tool_use.py).
tools = [
    {
        "name": "get_current_time",
        "description": "Returns the current UTC date and time.",
        "input_schema": {"type": "object", "properties": {}}
    },
    {
        "name": "calculate",
        "description": "Evaluate a simple arithmetic expression and return the numeric result.",
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A Python arithmetic expression, e.g. '(3 + 5) * 2'"
                }
            },
            "required": ["expression"]
        }
    }
]

def execute_tool(name: str, inputs: dict) -> str:
    if name == "get_current_time":
        return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    if name == "calculate":
        try:
            result = eval(inputs["expression"], {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"Error: {e}"
    return f"Unknown tool: {name}"


def handle_parallel_tools(response_content: list) -> list:
    """Process all tool_use blocks from one response in parallel."""
    tool_calls = [b for b in response_content if b.type == "tool_use"]

    def execute(block):
        result = execute_tool(block.name, block.input)
        return {"type": "tool_result", "tool_use_id": block.id, "content": result}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        return list(executor.map(execute, tool_calls))

if __name__ == "__main__":
    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=1024,
        tools=tools,
        messages=[{"role": "user", "content": "What time is it and what is 99 * 99?"}]
    )
    if response.stop_reason == "tool_use":
        results = handle_parallel_tools(response.content)
        print("Tool results:", results)
