import httpx
from mcp.server.fastmcp import FastMCP
from bs4 import BeautifulSoup
import os

mcp = FastMCP("research-tools")

BRAVE_KEY = os.getenv("BRAVE_SEARCH_API_KEY", "")


@mcp.tool()
async def web_search(query: str, count: int = 5) -> list[dict]:
    """Search the web and return titles + snippets + URLs."""
    async with httpx.AsyncClient() as client:
        r = await client.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": query, "count": count},
            headers={"X-Subscription-Token": BRAVE_KEY},
        )
        r.raise_for_status()
        results = r.json().get("web", {}).get("results", [])
        return [
            {"title": x["title"], "url": x["url"], "snippet": x.get("description", "")}
            for x in results
        ]


@mcp.tool()
async def fetch_url(url: str, max_chars: int = 8000) -> str:
    """Fetch a URL and return cleaned text content."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
        r = await client.get(url, headers={"User-Agent": "ResearchBot/1.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = soup.get_text(" ", strip=True)
        return text[:max_chars]


if __name__ == "__main__":
    mcp.run(transport="stdio")
