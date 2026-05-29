"""
Cloud Run deployment helper — Chapter 13.

Cloud Run is the fastest path to production for Claude applications:
  - One command: `gcloud run deploy` builds the image, deploys, and returns a URL
  - Scales to zero when idle (~$0/month baseline)
  - Cold start: ~1-2s for a slim Python image
  - Secrets injected at runtime via Secret Manager — never baked into the image

Deploy command (run from the repo root):

  gcloud run deploy claude-app \\
    --source . \\
    --region europe-west1 \\
    --allow-unauthenticated \\
    --set-secrets ANTHROPIC_API_KEY=anthropic-key:latest \\
    --memory 1Gi --cpu 2 \\
    --concurrency 80 \\
    --min-instances 0 --max-instances 10

This script shows how to store the secret and verify the deployed service is reachable.
"""

import os
import subprocess
import sys
import urllib.request


def create_secret(api_key: str, secret_name: str = "anthropic-key") -> None:
    """Store the Anthropic API key in GCP Secret Manager (run once)."""
    result = subprocess.run(
        ["gcloud", "secrets", "describe", secret_name],
        capture_output=True
    )
    if result.returncode == 0:
        print(f"Secret '{secret_name}' already exists — skipping creation.")
        return

    subprocess.run(
        ["gcloud", "secrets", "create", secret_name, "--data-file=-"],
        input=api_key.encode(),
        check=True,
    )
    print(f"Secret '{secret_name}' created.")


def get_service_url(service_name: str = "claude-app", region: str = "europe-west1") -> str:
    """Retrieve the public URL of a deployed Cloud Run service."""
    result = subprocess.run(
        [
            "gcloud", "run", "services", "describe", service_name,
            "--region", region,
            "--format", "value(status.url)",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def health_check(url: str) -> bool:
    """Hit /health and confirm the service is up."""
    try:
        with urllib.request.urlopen(f"{url}/health", timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


if __name__ == "__main__":
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        sys.exit("Set ANTHROPIC_API_KEY before running this script.")

    print("Step 1 — storing secret in Secret Manager...")
    create_secret(api_key)

    print("Step 2 — fetching deployed service URL...")
    try:
        url = get_service_url()
        print(f"Service URL: {url}")

        print("Step 3 — health check...")
        ok = health_check(url)
        print("Service healthy." if ok else "Service not responding.")
    except subprocess.CalledProcessError:
        print("Service not yet deployed. Run the gcloud deploy command shown in the docstring.")
