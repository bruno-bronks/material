import httpx

BASE_URL = "https://aflow.org/API/aflux/"


def search_by_species(elements: list[str], limit: int = 5) -> list[dict]:
    if not elements:
        return []

    species = ",".join(elements)
    query = (
        f"species({species}),format(json),paging(1,{limit}),"
        "enthalpy_formation_atom,Egap,density,spacegroup_relax"
    )

    try:
        response = httpx.get(f"{BASE_URL}?{query}", timeout=20)
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    data = response.json()
    if not isinstance(data, dict):
        return []

    results = []
    for entry in list(data.values())[:limit]:
        results.append(
            {
                "source": "aflow",
                "material_name": entry.get("compound"),
                "composition": entry.get("compound"),
                "crystal_structure": entry.get("spacegroup_relax"),
                "band_gap": entry.get("Egap"),
                "density": entry.get("density"),
                "formation_energy": entry.get("enthalpy_formation_atom"),
            }
        )
    return results
