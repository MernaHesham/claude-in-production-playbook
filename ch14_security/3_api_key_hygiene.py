"""
API key hygiene — Chapter 14.

Rules:
  - Never hardcode keys in source code or Docker images
  - Never log the key value — not even partially
  - Rotate keys on suspected exposure; revoke immediately via console.anthropic.com
  - Inject at runtime via Secret Manager (GCP), Secrets Manager (AWS), or env vars

GCP one-liner to store the key:
  echo -n "sk-ant-xxx" | gcloud secrets create anthropic-key --data-file=-

AWS one-liner:
  aws secretsmanager create-secret --name anthropic-key \\
    --secret-string '{"api_key":"sk-ant-xxx"}'
"""

import os
import re
import anthropic
from dotenv import load_dotenv

load_dotenv()

_SK_PATTERN = re.compile(r"sk-ant-[A-Za-z0-9\-]+")


def load_key_from_gcp(secret_name: str = "anthropic-key") -> str:
    """Fetch the API key from GCP Secret Manager at runtime."""
    from google.cloud import secretmanager  # pip install google-cloud-secret-manager

    project_id = os.environ["GCP_PROJECT_ID"]
    sm = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
    response = sm.access_secret_version(request={"name": name})
    return response.payload.data.decode("utf-8")


def load_key_from_aws(secret_name: str = "anthropic-key") -> str:
    """Fetch the API key from AWS Secrets Manager at runtime."""
    import boto3, json  # noqa: E401

    client = boto3.client("secretsmanager")
    secret = client.get_secret_value(SecretId=secret_name)
    return json.loads(secret["SecretString"])["api_key"]


def assert_no_key_in_logs(text: str) -> str:
    """Redact any API key that accidentally appears in log output."""
    return _SK_PATTERN.sub("[REDACTED]", text)


def get_client() -> anthropic.Anthropic:
    """Resolve the API key and return a configured client. Never log the key."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. "
            "Inject it via Secret Manager or a .env file — never hardcode it."
        )
    # Validate format without logging the value
    if not api_key.startswith("sk-ant-"):
        raise ValueError("API key format looks wrong. Check Secret Manager.")
    return anthropic.Anthropic(api_key=api_key)


if __name__ == "__main__":
    client = get_client()

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=64,
        messages=[{"role": "user", "content": "Say 'key hygiene confirmed' and nothing else."}]
    )
    output = response.content[0].text

    # Defensive: scrub any key that might appear in model output
    safe_output = assert_no_key_in_logs(output)
    print(safe_output)

    # Demonstrate redaction
    demo = f"Imagine a log line leaking: sk-ant-api03-abc123xyz"
    print(assert_no_key_in_logs(demo))
