from dotenv import load_dotenv
import anthropic
import json
from typing import Callable, Any
from dataclasses import dataclass

load_dotenv()
client = anthropic.Anthropic()


@dataclass
class AgentStep:
    step_num: int
    thought: str
    action: str
    action_input: dict
    observation: str


class ReActAgent:
    def __init__(
        self,
        tools: list[dict],
        tool_executor: Callable[[str, dict], Any],
        system_prompt: str,
        model: str = "claude-sonnet-4-6",
        max_steps: int = 15
    ):
        self.tools = tools
        self.tool_executor = tool_executor
        self.system_prompt = system_prompt
        self.model = model
        self.max_steps = max_steps
        self.steps: list[AgentStep] = []

    def run(self, goal: str) -> str:
        messages = [{"role": "user", "content": goal}]
        self.steps = []

        for step in range(self.max_steps):
            response = client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                tools=self.tools,
                messages=messages
            )

            if response.stop_reason == "end_turn":
                return next(b.text for b in response.content if b.type == "text")

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []

                for block in response.content:
                    if block.type == "tool_use":
                        try:
                            result = self.tool_executor(block.name, block.input)
                            result_str = json.dumps(result) if not isinstance(result, str) else result
                        except Exception as e:
                            result_str = f"ERROR: {e}"

                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_str
                        })
                        self.steps.append(AgentStep(
                            step_num=step + 1,
                            thought="",
                            action=block.name,
                            action_input=block.input,
                            observation=result_str
                        ))

                messages.append({"role": "user", "content": tool_results})

        return "Max steps reached without a final answer."


if __name__ == "__main__":
    import datetime

    demo_tools = [
        {
            "name": "get_date",
            "description": "Returns the current date.",
            "input_schema": {"type": "object", "properties": {}}
        }
    ]

    def demo_executor(name, inputs):
        if name == "get_date":
            return datetime.date.today().isoformat()
        return f"Unknown tool: {name}"

    agent = ReActAgent(
        tools=demo_tools,
        tool_executor=demo_executor,
        system_prompt="You are a helpful assistant. Use tools when needed.",
    )
    result = agent.run("What is today's date?")
    print(result)
    print(f"Steps taken: {len(agent.steps)}")
