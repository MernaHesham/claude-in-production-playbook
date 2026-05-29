from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

AGENT_SYSTEM = """
You are a research agent with access to the following tools:
- search_web(query: str) → list of search results with titles and snippets
- fetch_page(url: str) → full text content of a webpage
- save_finding(key: str, value: str) → persists a key-value pair

Your goal: answer the user's research question completely and accurately.

<process>
1. Decompose the question into 3-5 sub-questions
2. For each sub-question: search, fetch relevant pages, save findings
3. Synthesise all saved findings into a final answer
4. Cite every factual claim with the URL it came from
</process>

<termination>
Stop when all sub-questions have answers supported by at least one source.
If after 10 tool calls you cannot find an answer, say so explicitly — do not fabricate.
</termination>

<error_handling>
If a tool returns an error or empty result: try a different search query or URL.
After 3 failures on the same sub-question, mark it as "unanswerable" and move on.
</error_handling>
"""

if __name__ == "__main__":
    # Demonstrate the system prompt structure without executing tools
    print("Agentic system prompt loaded.")
    print(f"System prompt length: {len(AGENT_SYSTEM)} chars")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        system=AGENT_SYSTEM,
        messages=[{"role": "user", "content": "What tools do you have available and what is your research process?"}]
    )
    print(response.content[0].text)
