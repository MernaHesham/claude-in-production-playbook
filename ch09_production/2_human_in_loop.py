from dotenv import load_dotenv
from langgraph.graph import StateGraph, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

load_dotenv()

APPROVAL_REQUIRED = {"send_email", "delete_record", "make_payment"}


def execute_tool(name: str, args: dict) -> str:
    """Simulate tool execution — replace with real implementations."""
    return f"Executed {name} with args {args}"


def tool_node_with_approval(state: MessagesState):
    last_message = state["messages"][-1]
    tool_calls = last_message.tool_calls

    for call in tool_calls:
        if call["name"] in APPROVAL_REQUIRED:
            approval = interrupt({
                "type": "approval_request",
                "tool": call["name"],
                "args": call["args"],
                "message": f"Claude wants to call {call['name']}. Approve?"
            })
            if not approval.get("approved"):
                return {"messages": [{
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": "Action cancelled by user."
                }]}
            else:
                result = execute_tool(call["name"], call["args"])
                return {"messages": [{
                    "role": "tool",
                    "tool_call_id": call["id"],
                    "content": str(result)
                }]}


if __name__ == "__main__":
    print("Human-in-the-loop pattern loaded.")
    print(f"Actions requiring approval: {APPROVAL_REQUIRED}")
    print("Integrate tool_node_with_approval as a LangGraph node with MemorySaver checkpointer.")
