from dotenv import load_dotenv
import anthropic
import json

load_dotenv()
client = anthropic.Anthropic()


def critic_review(original_task: str, agent_output: str) -> dict:
    """Have an independent agent review the primary agent's output."""
    review = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system="""You are a quality reviewer. Your only job is to critically evaluate
work produced by another AI agent. Be rigorous and specific.

Return JSON:
{
  "passed": true/false,
  "issues": [{"severity": "critical|major|minor", "description": "...", "fix": "..."}],
  "overall_score": 0-10
}
If passed is false, list at least one critical or major issue.""",
        messages=[{
            "role": "user",
            "content": f"Original task:\n{original_task}\n\nAgent output:\n{agent_output}"
        }]
    )
    return json.loads(review.content[0].text)


def generate_with_critic(task: str, max_revisions: int = 2) -> str:
    """Generate, critique, revise — up to max_revisions times."""
    output = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=2048,
        messages=[{"role": "user", "content": task}]
    ).content[0].text

    for revision in range(max_revisions):
        review = critic_review(task, output)
        if review["passed"]:
            break
        issues_text = "\n".join([
            f"- [{i['severity'].upper()}] {i['description']}. Fix: {i['fix']}"
            for i in review["issues"]
        ])
        output = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=2048,
            messages=[{"role": "user", "content":
                f"Revise your previous response to fix these issues:\n{issues_text}\n\nOriginal task: {task}"
            }]
        ).content[0].text

    return output


if __name__ == "__main__":
    result = generate_with_critic(
        "Write a 200-word executive summary of why RAG outperforms fine-tuning for enterprise knowledge retrieval."
    )
    print(result)
