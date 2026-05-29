import sys
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

def stream_response(prompt: str, system: str = "") -> str:
    full_text = ""
    kwargs = {
        "model": "claude-sonnet-4-6",
        "max_tokens": 2048,
        "messages": [{"role": "user", "content": prompt}]
    }
    if system:
        kwargs["system"] = system
    with client.messages.stream(**kwargs) as stream:
        for text in stream.text_stream:
            sys.stdout.write(text)
            sys.stdout.flush()
            full_text += text
    print()
    return full_text

if __name__ == "__main__":
    stream_response("Explain vector embeddings in simple terms.", system="Be concise.")
