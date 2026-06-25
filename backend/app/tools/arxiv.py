import feedparser
import httpx

BASE_URL = "https://export.arxiv.org/api/query"


def search_papers(query: str, limit: int = 5) -> list[dict]:
    """Mistura resultados por relevância com os mais recentes (sortBy=submittedDate).

    Sem isso, "pesquisas recentes sobre X" podia devolver só o artigo mais relevante
    por palavra-chave mesmo que tivesse anos — o paper_search.jinja2 sempre pede
    "descobertas recentes", então sempre garantimos pelo menos alguns candidatos novos.
    """
    relevance_hits = _query(query, limit=limit, sort_by_date=False)
    recent_hits = _query(query, limit=max(2, limit // 2), sort_by_date=True)

    seen_urls = set()
    merged = []
    for hit in relevance_hits + recent_hits:
        if hit["url"] in seen_urls:
            continue
        seen_urls.add(hit["url"])
        merged.append(hit)

    return merged[: limit + 2]


def _query(query: str, limit: int, sort_by_date: bool) -> list[dict]:
    params = {
        "search_query": f"all:{query}",
        "start": 0,
        "max_results": limit,
    }
    if sort_by_date:
        params["sortBy"] = "submittedDate"
        params["sortOrder"] = "descending"

    try:
        response = httpx.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    feed = feedparser.parse(response.text)
    return [
        {
            "source": "arxiv",
            "title": entry.get("title", "").replace("\n", " ").strip(),
            "authors": [author.get("name") for author in entry.get("authors", [])],
            "year": entry.get("published", "")[:4],
            "doi": entry.get("arxiv_doi", ""),
            "abstract": entry.get("summary", "").replace("\n", " ").strip(),
            "url": entry.get("link"),
        }
        for entry in feed.entries
    ]
