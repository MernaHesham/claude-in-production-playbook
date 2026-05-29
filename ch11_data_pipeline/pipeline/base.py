from dataclasses import dataclass, field
from typing import Any
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()


@dataclass
class Artefact:
    kind: str      # "data" | "chart" | "report"
    content: Any
    meta: dict = field(default_factory=dict)


class BaseAgent:
    model = "claude-sonnet-4-6"
    system = ""
    tools = []

    def run(self, prompt: str, context: list = None) -> Artefact:
        context = context or []
        ctx = "\n\n".join(f"[{a.kind.upper()}]\n{a.content}" for a in context)
        messages = [{"role": "user", "content": f"{ctx}\n\n{prompt}" if ctx else prompt}]

        while True:
            resp = client.messages.create(
                model=self.model, max_tokens=4096,
                system=self.system, tools=self.tools, messages=messages
            )
            messages.append({"role": "assistant", "content": resp.content})

            if resp.stop_reason == "end_turn":
                text = next(b.text for b in resp.content if b.type == "text")
                return self._parse(text)

            results = []
            for b in resp.content:
                if b.type == "tool_use":
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": b.id,
                        "content": str(self._dispatch_tool(b.name, b.input))
                    })
            messages.append({"role": "user", "content": results})

    def _dispatch_tool(self, name, inputs):
        raise NotImplementedError

    def _parse(self, text) -> Artefact:
        raise NotImplementedError
