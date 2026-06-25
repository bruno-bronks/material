import httpx
from pymatgen.core import Structure

from app.config import get_settings

BASE_URL = "https://api.materialsproject.org/materials/summary/"


def search_by_formula(formula: str, limit: int = 5) -> list[dict]:
    settings = get_settings()
    if not settings.mp_api_key:
        return []

    params = {
        "formula": formula,
        "_limit": limit,
        "_fields": "material_id,formula_pretty,density,band_gap,energy_above_hull,symmetry",
    }
    headers = {"X-API-KEY": settings.mp_api_key}

    try:
        response = httpx.get(BASE_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()
    except httpx.HTTPError:
        return []

    results = []
    for entry in response.json().get("data", []):
        symmetry = entry.get("symmetry") or {}
        results.append(
            {
                "source": "materials_project",
                "material_id": entry.get("material_id"),
                "material_name": entry.get("formula_pretty"),
                "composition": entry.get("formula_pretty"),
                "density": entry.get("density"),
                "band_gap": entry.get("band_gap"),
                "energy_above_hull": entry.get("energy_above_hull"),
                "crystal_structure": symmetry.get("crystal_system"),
            }
        )
    return results


def get_structure(material_id: str) -> Structure | None:
    """Estrutura cristalina completa (posições atômicas), usada como input do GNN."""
    settings = get_settings()
    if not settings.mp_api_key:
        return None

    from mp_api.client import MPRester

    try:
        with MPRester(settings.mp_api_key, mute_progress_bars=True) as mpr:
            return mpr.get_structure_by_material_id(material_id)
    except Exception:
        return None
