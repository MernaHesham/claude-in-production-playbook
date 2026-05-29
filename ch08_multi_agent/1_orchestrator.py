from dotenv import load_dotenv
import anthropic
import concurrent.futures
import json
from dataclasses import dataclass

load_dotenv()
client = anthropic.Anthropic()


@dataclass
class SubTask:
    id: str
    description: str
    agent_role: str


def orchestrate(goal: str) -> str:
    # Step 1: Decompose the goal
    decomp = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2048,
        system="""You are a task orchestrator. Given a complex goal, decompose it
into 2-5 independent subtasks that can be worked on in parallel.

Return JSON: {"subtasks": [{"id": "t1", "description": "...", "agent_role": "..."}]}""",
        messages=[{"role": "user", "content": goal}]
    )

    subtasks_data = json.loads(decomp.content[0].text)
    subtasks = [SubTask(**t) for t in subtasks_data["subtasks"]]

    # Step 2: Run worker agents in parallel
    def run_worker(subtask: SubTask) -> tuple[str, str]:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=f"You are a {subtask.agent_role}. Complete the assigned task thoroughly.",
            messages=[{"role": "user", "content": subtask.description}]
        )
        return subtask.id, response.content[0].text

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        worker_results = dict(pool.map(run_worker, subtasks))

    # Step 3: Synthesise
    context = "\n\n".join([
        f"[{t.id}] {t.description}:\n{worker_results[t.id]}"
        for t in subtasks
    ])

    synthesis = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=3000,
        system="Synthesise the worker outputs into a single coherent, well-structured response for the user.",
        messages=[{"role": "user", "content": f"Goal: {goal}\n\nWorker outputs:\n{context}"}]
    )
    return synthesis.content[0].text


if __name__ == "__main__":
    result = orchestrate("Write a market analysis of the EU AI regulation landscape in 2025")
    print(result)
