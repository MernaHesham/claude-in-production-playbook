"""
Vision: Claude can read images — screenshots, charts, diagrams, documents.
Works with URLs (Claude fetches) or base64 (you encode).
Supported formats: JPEG, PNG, GIF, WebP. Max 5MB per image. Up to 20 images per request.
"""
import base64
import httpx
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

SAMPLE_IMAGE_URL = "https://www.python.org/static/img/python-logo.png"

def describe_image_from_url(url: str, question: str = "Describe this image in one sentence.") -> str:
    """Send an image URL to Claude — Claude fetches it."""
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "url", "url": url}},
                {"type": "text", "text": question}
            ]
        }]
    )
    return response.content[0].text

def describe_image_from_bytes(image_bytes: bytes, media_type: str, question: str) -> str:
    """Send an image as base64 — useful for local files."""
    image_b64 = base64.standard_b64encode(image_bytes).decode("utf-8")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": image_b64}},
                {"type": "text", "text": question}
            ]
        }]
    )
    return response.content[0].text

if __name__ == "__main__":
    print("=== URL image ===")
    print(describe_image_from_url(SAMPLE_IMAGE_URL))

    print("\n=== Base64 image ===")
    image_bytes = httpx.get(SAMPLE_IMAGE_URL).content
    print(describe_image_from_bytes(image_bytes, "image/png", "What colours are dominant?"))
