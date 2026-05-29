from dotenv import load_dotenv
import structlog
from functools import wraps
from time import perf_counter
import anthropic

load_dotenv()
log = structlog.get_logger()
client = anthropic.Anthropic()

COST_PER_MTOK = {
    "claude-opus-4-7":          {"input": 0.015,  "output": 0.075},
    "claude-sonnet-4-6":        {"input": 0.003,  "output": 0.015},
    "claude-haiku-4-5-20251001": {"input": 0.0008, "output": 0.004},
}


def traced_api_call(func):
    """Decorator to log every Claude API call with latency and token usage."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = perf_counter()
        response = func(*args, **kwargs)
        elapsed = perf_counter() - start

        model = kwargs.get("model", "unknown")
        cost = estimate_cost(model, response.usage.input_tokens, response.usage.output_tokens)

        log.info(
            "claude_api_call",
            model=model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            stop_reason=response.stop_reason,
            latency_ms=round(elapsed * 1000),
            estimated_cost_usd=round(cost, 6),
        )
        return response
    return wrapper


def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    rates = COST_PER_MTOK.get(model, COST_PER_MTOK["claude-sonnet-4-6"])
    return (input_tokens * rates["input"] + output_tokens * rates["output"]) / 1_000_000


@traced_api_call
def create_message(**kwargs):
    return client.messages.create(**kwargs)


if __name__ == "__main__":
    response = create_message(
        model="claude-haiku-4-5-20251001",
        max_tokens=128,
        messages=[{"role": "user", "content": "Hello!"}]
    )
    print(response.content[0].text)
