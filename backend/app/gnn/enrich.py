from app.gnn.elastic import estimate_bulk_modulus
from app.gnn.predictor import predict_band_gap, predict_formation_energy
from app.tools import materials_project


def _mp_candidates(materials: list[dict]):
    for material in materials:
        if material.get("source") == "materials_project" and material.get("material_id"):
            yield material


def enrich_with_gnn(materials: list[dict], limit: int = 3) -> list[dict]:
    """V2: Structure -> Graph -> GNN -> Property Prediction (energia de formação + band gap).

    Só se aplica a candidatos vindos do Materials Project (únicos com
    material_id, necessário para buscar a estrutura cristalina completa).
    Barato (duas inferências por material, sem relaxação) — roda para todo
    material_search.
    """
    enriched = 0
    for material in _mp_candidates(materials):
        if enriched >= limit:
            break

        structure = materials_project.get_structure(material["material_id"])
        if structure is None:
            continue

        formation_energy = predict_formation_energy(structure)
        if formation_energy is not None:
            material["gnn_formation_energy_ev_atom"] = formation_energy

        # Só prevê band gap se ainda não tivermos um valor real (de banco de
        # dados) — não tem sentido sobrescrever um dado conhecido por uma estimativa.
        if material.get("band_gap") is None:
            band_gap = predict_band_gap(structure)
            if band_gap is not None:
                material["gnn_band_gap_ev"] = band_gap

        enriched += 1

    return materials


def enrich_with_bulk_modulus(materials: list[dict], limit: int = 1) -> list[dict]:
    """V3: módulo de compressibilidade via M3GNet + equação de estado.

    Bem mais caro que enrich_with_gnn (várias relaxações por material), por
    isso só roda para o(s) primeiro(s) candidato(s) e só quando chamado
    explicitamente pelo node_property_prediction — não é plugado no
    tools/router para não deixar todo intent lento.
    """
    enriched = 0
    for material in _mp_candidates(materials):
        if enriched >= limit:
            break

        structure = materials_project.get_structure(material["material_id"])
        if structure is None:
            continue

        bulk_modulus = estimate_bulk_modulus(structure)
        if bulk_modulus is not None:
            material["gnn_bulk_modulus_gpa"] = bulk_modulus
        enriched += 1

    return materials
