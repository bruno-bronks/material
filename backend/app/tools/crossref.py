import httpx

BASE_URL = "https://api.crossref.org/works"


def search_works(query: str, limit: int = 5) -> list[dict]:
    params = {"query": query, "rows": limit}

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
