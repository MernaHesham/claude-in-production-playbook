from dotenv import load_dotenv
import json
import redis
from datetime import datetime

load_dotenv()


class AgentMemory:
    """Persistent agent memory backed by Redis."""

    def __init__(self, agent_id: str, ttl_seconds: int = 86400):
        self.r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        self.key = f"agent:{agent_id}:memory"
        self.ttl = ttl_seconds

    def save(self, key: str, value: str):
        mem = self._load()
        mem[key] = {"value": value, "saved_at": datetime.utcnow().isoformat()}
        self.r.setex(self.key, self.ttl, json.dumps(mem))

    def get(self, key: str) -> str | None:
        mem = self._load()
        entry = mem.get(key)
        return entry["value"] if entry else None

    def as_context_string(self) -> str:
        mem = self._load()
        if not mem:
            return "No memory stored yet."
        lines = [f"- {k}: {v['value']}" for k, v in mem.items()]
        return "\n".join(lines)

    def _load(self) -> dict:
        raw = self.r.get(self.key)
        return json.loads(raw) if raw else {}


if __name__ == "__main__":
    print("AgentMemory requires a running Redis instance.")
    print("Usage:")
    print("  mem = AgentMemory('user-123')")
    print("  mem.save('preferred_language', 'Python')")
    print("  print(mem.as_context_string())")
