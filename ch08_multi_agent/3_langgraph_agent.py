from dotenv import load_dotenv
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatAnthropic(model="claude-sonnet-4-6")


@tool
def search_web(query: str) -> str:
    """Search the web for current information."""
    return f"Search results for '{query}': [placeholder — integrate Tavily or SerpAPI in production]"


@tool
def write_file(filename: str, content: str) -> str:
    """Write content to a file."""
    with open(filename, "w") as f:
        f.write(content)
    return f"Written {len(content)} chars to {filename}"


tools = [search_web, write_file]
llm_with_tools = llm.bind_tools(tools)


def agent_node(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


# Build the graph
builder = StateGraph(MessagesState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(tools))
builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
graph = builder.compile()


if __name__ == "__main__":
    result = graph.invoke({
        "messages": [HumanMessage(content="Research AI regulation in the EU and save a brief summary to eu_ai_brief.md")]
    })
    print(result["messages"][-1].content)
