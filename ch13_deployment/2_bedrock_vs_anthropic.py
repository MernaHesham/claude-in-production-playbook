"""
Anthropic API vs AWS Bedrock — Chapter 13.

Decision guide:
  Anthropic API  → same-day model access, startups, fastest iteration
  AWS Bedrock    → EU data residency, existing AWS commitment, FedRAMP/HIPAA

| Factor          | Anthropic API               | AWS Bedrock                         |
|-----------------|----------------------------|-------------------------------------|
| Latest models   | Same-day access             | Weeks-to-months lag                 |
| Data residency  | US-only today               | Multi-region (EU, AP)               |
| Compliance      | SOC 2, GDPR, HIPAA BAA     | SOC 2, HIPAA, FedRAMP               |
| Best for        | Startups, fast iteration    | Enterprises with EU data rules      |

This script shows the same call made through both APIs so you can compare them side-by-side.
Install boto3 (`pip install boto3`) and configure AWS credentials to run the Bedrock path.
"""

import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

PROMPT = "Explain prompt caching in one paragraph, suitable for a CTO audience."
MODEL_ANTHROPIC = "claude-sonnet-4-6"
MODEL_BEDROCK = "anthropic.claude-sonnet-4-6-20250514-v1:0"  # Bedrock model ID format


def call_anthropic_api(prompt: str) -> str:
    client = anthropic.Anthropic()
    response = client.messages.create(
        model=MODEL_ANTHROPIC,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text


def call_bedrock(prompt: str) -> str:
    """Same call via AWS Bedrock — requires boto3 and AWS credentials."""
    import boto3, json  # noqa: E401

    bedrock = boto3.client(
        service_name="bedrock-runtime",
        region_name=os.getenv("AWS_REGION", "eu-west-1"),  # EU region for data residency
    )
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 512,
        "messages": [{"role": "user", "content": prompt}]
    })
    response = bedrock.invoke_model(modelId=MODEL_BEDROCK, body=body)
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]


if __name__ == "__main__":
    print("=== Anthropic API ===")
    print(call_anthropic_api(PROMPT))

    print("\n=== AWS Bedrock (requires boto3 + AWS credentials) ===")
    try:
        print(call_bedrock(PROMPT))
    except ImportError:
        print("boto3 not installed. Run: pip install boto3")
    except Exception as e:
        print(f"Bedrock call failed: {e}")
        print("Ensure AWS credentials and region are configured.")
