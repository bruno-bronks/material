import httpx

BASE_URL = "https://oqmd.org/oqmdapi/formationenergy"


def search_by_composition(composition: str, limit: int = 5) -> list[dict]:
    params = {
        "composition": composition,
        "limit": limit,
        "fields": "name,delta_e,stability,spacegroup,band_gap",
    }

    try:
        response = httpx.get(BASE_URL, params=params, timeout=15)
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    results = []
    for entry in response.json().get("data", []):
        results.append(
            {
                "source": "oqmd",
                "material_name": entry.get("name"),
                "composition": entry.get("name"),
                "formation_energy": entry.get("delta_e"),
                "stability": entry.get("stability"),
                "crystal_structure": entry.get("spacegroup"),
                "band_gap": entry.get("band_gap"),
            }
        )
    return results
