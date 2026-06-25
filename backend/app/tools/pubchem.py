import httpx

BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"


def search_by_name(name: str) -> list[dict]:
    url = f"{BASE_URL}/compound/name/{name}/property/MolecularFormula,MolecularWeight,IUPACName/JSON"
    try:
        response = httpx.get(url, timeout=15)
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    properties = response.json().get("PropertyTable", {}).get("Properties", [])
    results = []
    for entry in properties:
        results.append(
            {
                "source": "pubchem",
                "cid": entry.get("CID"),
                "material_name": entry.get("IUPACName") or name,
                "composition": entry.get("MolecularFormula"),
                "molecular_weight": entry.get("MolecularWeight"),
            }
        )
    return results
