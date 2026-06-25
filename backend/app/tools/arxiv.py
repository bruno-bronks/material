import feedparser
import httpx

BASE_URL = "https://export.arxiv.org/api/query"


def search_papers(query: str, limit: int = 5) -> list[dict]:
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": limit,
    }

    try:
        response = httpx.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    feed = feedparser.parse(response.text)
    results = []
    for entry in feed.entries:
        results.append(
            {
                "source": "arxiv",
                "title": entry.get("title", "").replace("\n", " ").strip(),
                "authors": [author.get("name") for author in entry.get("authors", [])],
                "year": entry.get("published", "")[:4],
                "doi": entry.get("arxiv_doi", ""),
                "abstract": entry.get("summary", "").replace("\n", " ").strip(),
                "url": entry.get("link"),
            }
        )
    return results
