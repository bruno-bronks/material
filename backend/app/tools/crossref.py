import httpx

BASE_URL = "https://api.crossref.org/works"


def search_works(query: str, limit: int = 5) -> list[dict]:
    """Mistura resultados por relevância com os mais recentes (sort=published).

    Mesma razão do arxiv.py: "pesquisas recentes" não deve depender só do ranking
    de relevância da API, que pode trazer um resultado antigo bem casado por palavra-chave.
    """
    relevance_hits = _query(query, limit=limit, sort_by_date=False)
    recent_hits = _query(query, limit=max(2, limit // 2), sort_by_date=True)

    seen_dois = set()
    merged = []
    for hit in relevance_hits + recent_hits:
        key = hit["doi"] or hit["title"]
        if key in seen_dois:
            continue
        seen_dois.add(key)
        merged.append(hit)

    return merged[: limit + 2]


def _query(query: str, limit: int, sort_by_date: bool) -> list[dict]:
    params = {"query": query, "rows": limit}
    if sort_by_date:
        params["sort"] = "published"
        params["order"] = "desc"

    try:
        response = httpx.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    results = []
    for entry in response.json().get("message", {}).get("items", []):
        title = entry.get("title") or [""]
        authors = [
            " ".join(filter(None, [author.get("given"), author.get("family")]))
            for author in entry.get("author", [])
        ]
        year = None
        date_parts = (entry.get("issued") or {}).get("date-parts")
        if date_parts and date_parts[0]:
            year = date_parts[0][0]

        results.append(
            {
                "source": "crossref",
                "title": title[0],
                "authors": authors,
                "year": year,
                "doi": entry.get("DOI", ""),
                "abstract": entry.get("abstract", ""),
            }
        )
    return results
