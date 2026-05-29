"""
Batch API: submit up to 10,000 requests in one call.
50% cheaper than regular API. Results ready in minutes to hours.
Use for: bulk document processing, running evals, nightly jobs.
"""
import time
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

def submit_batch(tickets: list[str]) -> str:
    """Submit a batch of support ticket classification requests."""
    requests = [
        {
            "custom_id": f"support-{i}",
            "params": {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 128,
                "system": "Classify this support ticket as: billing, technical, feature, or general. Reply with one word only.",
                "messages": [{"role": "user", "content": ticket}]
            }
        }
        for i, ticket in enumerate(tickets)
    ]
    batch = client.messages.batches.create(requests=requests)
    print(f"Batch submitted: {batch.id}")
    print(f"Status: {batch.processing_status}")
    return batch.id

def poll_batch(batch_id: str) -> dict:
    """Poll until batch completes, then return results."""
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        print(f"Status: {batch.processing_status} | "
              f"Succeeded: {batch.request_counts.succeeded} | "
              f"Processing: {batch.request_counts.processing}")
        if batch.processing_status == "ended":
            break
        time.sleep(5)

    results = {}
    for result in client.messages.batches.results(batch_id):
        if result.result.type == "succeeded":
            results[result.custom_id] = result.result.message.content[0].text.strip()
        else:
            results[result.custom_id] = f"ERROR: {result.result.error}"
    return results

if __name__ == "__main__":
    sample_tickets = [
        "I was charged twice for the same month. This is unacceptable.",
        "The dashboard is not loading. I've tried three browsers.",
        "Can you add Slack integration?",
        "How do I export my data?",
        "My API key stopped working.",
    ]
    batch_id = submit_batch(sample_tickets)
    print("\nPolling for results...")
    results = poll_batch(batch_id)
    print("\nResults:")
    for custom_id, classification in results.items():
        print(f"  {custom_id}: {classification}")
