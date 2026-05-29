import time
from dotenv import load_dotenv
import anthropic
from anthropic import APIStatusError, APIConnectionError, APITimeoutError

load_dotenv()
client = anthropic.Anthropic()

def resilient_call(
    messages: list,
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 1024,
    max_retries: int = 3,
    fallback_model: str = "claude-haiku-4-5-20251001"
) -> str:
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model=model, max_tokens=max_tokens, messages=messages
            )
            return response.content[0].text
        except APIStatusError as e:
            if e.status_code == 429:
                wait = 2 ** attempt
                print(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            elif e.status_code >= 500:
                if attempt == max_retries - 1 and model != fallback_model:
                    print(f"Falling back to {fallback_model}")
                    model = fallback_model
                time.sleep(1)
            else:
                raise
        except (APIConnectionError, APITimeoutError):
            time.sleep(2 ** attempt)
    raise RuntimeError("All retries exhausted.")

if __name__ == "__main__":
    result = resilient_call([{"role": "user", "content": "Hello!"}])
    print(result)
