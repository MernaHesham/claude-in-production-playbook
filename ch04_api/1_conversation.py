from dataclasses import dataclass, field
from typing import List, Dict, Any
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

@dataclass
class Conversation:
    model: str = "claude-sonnet-4-6"
    system: str = ""
    messages: List[Dict] = field(default_factory=list)
    max_tokens: int = 2048
    max_history: int = 40

    def chat(self, user_input: str) -> str:
        self.messages.append({"role": "user", "content": user_input})
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": self.messages
        }
        if self.system:
            kwargs["system"] = self.system
        response = client.messages.create(**kwargs)
        assistant_text = response.content[0].text
        self.messages.append({"role": "assistant", "content": assistant_text})
        return assistant_text

if __name__ == "__main__":
    conv = Conversation(system="You are a Python tutor for data scientists.")
    print(conv.chat("What is a context manager?"))
    print("\n---\n")
    print(conv.chat("Show me an example with file I/O."))
