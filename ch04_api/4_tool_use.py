import datetime
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

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

def run_agent(user_message: str) -> str:
    messages = [{"role": "user", "content": user_message}]
    for _ in range(10):
        response = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=1024,
            tools=tools, messages=messages
        )
        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if b.type == "text")
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result
                    })
            messages.append({"role": "user", "content": tool_results})
    return "Max iterations reached."

if __name__ == "__main__":
    print(run_agent("What time is it right now, and what is 17 * 23 + 8?"))
