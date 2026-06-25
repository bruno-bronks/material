import httpx

from app.config import get_settings

BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"


def search_papers(query: str, limit: int = 5) -> list[dict]:
    settings = get_settings()
    headers = {"x-api-key": settings.semantic_scholar_api_key} if settings.semantic_scholar_api_key else {}
    params = {
        "query": query,
        "limit": limit,
        "fields": "title,authors,year,externalIds,abstract,venue",
    }

    try:
        response = httpx.get(BASE_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    results = []
    for entry in response.json().get("data", []):
        results.append(
            {
                "source": "semantic_scholar",
                "title": entry.get("title"),
                "authors": [a.get("name") for a in entry.get("authors", [])],
                "year": entry.get("year"),
                "doi": (entry.get("externalIds") or {}).get("DOI", ""),
                "abstract": entry.get("abstract") or "",
                "venue": entry.get("venue"),
            }
        )
    return results
