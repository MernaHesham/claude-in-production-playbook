from dotenv import load_dotenv
import json
import uuid
import anthropic

load_dotenv()
client = anthropic.Anthropic()


class InMemoryStore:
    """Simple in-memory session store for development. Replace with Redis in production."""
    def __init__(self):
        self._data = {}

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value, ttl=None):
        self._data[key] = value

    def delete(self, key):
        self._data.pop(key, None)


class StatefulAgent:
    """Agent that persists conversation state across requests."""

    def __init__(self, session_store=None):
        self.store = session_store or InMemoryStore()
        self.system = "You are a helpful assistant with memory across sessions."

    def chat(self, session_id: str, user_message: str) -> str:
        history = self.store.get(session_id) or []
        history.append({"role": "user", "content": user_message})

        # Trim to last 40 messages to keep context bounded
        trimmed = history[-40:]

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=self.system,
            messages=trimmed
        )
        assistant_reply = response.content[0].text
        history.append({"role": "assistant", "content": assistant_reply})

        self.store.set(session_id, history, ttl=86400)
        return assistant_reply

    def new_session(self) -> str:
        return str(uuid.uuid4())


if __name__ == "__main__":
    agent = StatefulAgent()
    sid = agent.new_session()
    print(f"Session: {sid}")
    print(agent.chat(sid, "My name is Alice and I'm a data scientist."))
    print(agent.chat(sid, "What is my name and role?"))
