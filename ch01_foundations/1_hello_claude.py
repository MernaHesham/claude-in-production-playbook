from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

if __name__ == "__main__":
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": "Explain hybrid reasoning in one paragraph."}
        ]
    )

    print(response.content[0].text)
    print(f"Input tokens:  {response.usage.input_tokens}")
    print(f"Output tokens: {response.usage.output_tokens}")
