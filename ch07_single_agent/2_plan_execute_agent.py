"""
Plan & Execute pattern — different from ReAct.
ReAct: interleaves reasoning and action at every step (reactive).
Plan & Execute: first generates a complete plan, then executes each step in order.
Better for tasks where the full strategy should be decided upfront.
"""
import json
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()


def plan(goal: str, available_tools: list[str]) -> list[dict]:
    """Step 1: Generate a full execution plan before acting."""
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2048,
        system="""You are a task planner. Given a goal and available tools, produce a step-by-step plan.

Return ONLY a JSON array:
[{"step": 1, "tool": "<tool_name>", "input": "<what to pass>", "why": "<one sentence reason>"}]

Each step must use exactly one tool. Do not skip steps.""",
        messages=[{
            "role": "user",
            "content": f"Goal: {goal}\nAvailable tools: {', '.join(available_tools)}"
        }]
    )
    return json.loads(response.content[0].text)


def execute_step(step: dict, previous_results: list[str]) -> str:
    """Step 2: Execute one step, passing prior results as context."""
    context = "\n".join(f"Step {i+1} result: {r}" for i, r in enumerate(previous_results))
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=f"You are executing step {step['step']} of a plan. Use prior results as context.",
        messages=[{
            "role": "user",
            "content": f"""Prior results:
{context if context else 'None yet.'}

Current step: {step['why']}
Tool to use: {step['tool']}
Input: {step['input']}

Simulate executing this tool and return what it would produce."""
        }]
    )
    return response.content[0].text


def plan_and_execute(goal: str, tools: list[str]) -> dict:
    print(f"Planning: {goal}\n")
    steps = plan(goal, tools)
    print(f"Plan ({len(steps)} steps):")
    for s in steps:
        print(f"  {s['step']}. [{s['tool']}] {s['why']}")

    results = []
    for step in steps:
        print(f"\nExecuting step {step['step']}...")
        result = execute_step(step, results)
        results.append(result)
        print(f"  Result preview: {result[:100]}...")

    return {"steps": steps, "results": results, "final": results[-1] if results else ""}


if __name__ == "__main__":
    outcome = plan_and_execute(
        goal="Research the top 3 AI tools for customer support automation and write a comparison report",
        tools=["web_search", "fetch_url", "summarise_text", "write_report"]
    )
    print("\n=== Final Output ===")
    print(outcome["final"])
