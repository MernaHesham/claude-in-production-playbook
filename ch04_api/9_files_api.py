"""
Files API: upload a file once, reuse by ID across many requests.
Saves bandwidth and latency on repeated calls with the same document.
Files persist until deleted. No storage charge — only token usage when referenced.
"""
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

INVOICE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_invoice.txt")

def upload_file(file_path: str) -> str:
    """Upload a file and return its ID."""
    with open(file_path, "rb") as f:
        uploaded = client.beta.files.upload(
            file=(os.path.basename(file_path), f, "text/plain"),
        )
    print(f"Uploaded: {uploaded.id}  ({uploaded.filename})")
    return uploaded.id

def ask_about_file(file_id: str, question: str, model: str = "claude-sonnet-4-6") -> str:
    """Reference an uploaded file by ID in a message."""
    response = client.beta.messages.create(
        model=model,
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {"type": "document", "source": {"type": "file", "file_id": file_id}},
                {"type": "text", "text": question}
            ]
        }],
        betas=["files-api-2025-04-14"],
    )
    return response.content[0].text

def delete_file(file_id: str):
    client.beta.files.delete(file_id)
    print(f"Deleted: {file_id}")

if __name__ == "__main__":
    file_id = upload_file(INVOICE_PATH)

    print("\n=== Extraction ===")
    print(ask_about_file(
        file_id,
        "Extract: invoice number, vendor name, total amount, due date. Return as JSON."
    ))

    print("\n=== Reuse same file, different question ===")
    print(ask_about_file(
        file_id,
        "What is the VAT amount on this invoice?",
        model="claude-haiku-4-5-20251001"
    ))

    delete_file(file_id)
