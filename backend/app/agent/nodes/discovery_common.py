import math

from pymatgen.core import Element, Structure

from app.gnn.predictor import predict_formation_energy
from app.llm.client import get_llm
from app.prompts.loader import render_prompt
from app.schemas.discovery import SubstitutionTarget
from app.tools import materials_project
from app.tools.router import search_materials


def find_seed(question: str):
    """Acha um material real no Materials Project pra servir de base da hipótese.

    Retorna (material_id, Structure) ou None se não encontrar nenhum candidato
    com estrutura disponível (ex: sem MP_API_KEY, ou composição não encontrada).
    """
    materials = search_materials(question)
    candidate = next(
        (m for m in materials if m.get("source") == "materials_project" and m.get("material_id")),
        None,
    )
    if candidate is None:
        return None

    structure = materials_project.get_structure(candidate["material_id"])
    if structure is None:
        return None

    return candidate["material_id"], structure


def propose_target_element(
    question: str, base_composition: str, material_id: str, available_elements: str
) -> SubstitutionTarget:
    """Único uso de LLM na busca: decidir QUAL elemento da estrutura é o ponto de intervenção."""
    prompt = render_prompt(
        "discovery_hypothesis.jinja2",
        objective=question,
        base_composition=base_composition,
        base_material_id=material_id,
        available_elements=available_elements,
    )
    return get_llm().with_structured_output(SubstitutionTarget).invoke(prompt)


def rank_candidate_pool(structure: Structure, element_from: str, pool_size: int = 8) -> list[dict]:
    """V6 lite (active learning): gera candidatos quimicamente plausíveis para `element_from`
    e os ranqueia por energia de formação prevista pelo GNN (barato, ~1-3s cada) — só os
    melhores chegam a ser relaxados e julgados pelo LLM (caro, ~10-30s cada).
    """
    scored = []
    for element_to in _chemically_similar_elements(element_from, pool_size):
        candidate = structure.copy()
        candidate.replace_species({element_from: element_to})
        if candidate.composition.reduced_formula == structure.composition.reduced_formula:
            continue

        energy = predict_formation_energy(candidate)
        if energy is not None:
            scored.append({"element_to": element_to, "gnn_formation_energy_ev_atom": energy})

    return sorted(scored, key=lambda item: item["gnn_formation_energy_ev_atom"])


def _chemically_similar_elements(element_from: str, pool_size: int) -> list[str]:
    """Elementos parecidos por grupo, eletronegatividade e raio atômico — sem LLM, determinístico."""
    base = Element(element_from)

    def usable(el: Element) -> bool:
        return (
            el != base
            and not el.is_noble_gas
            and not el.is_radioactive
            and el.atomic_radius is not None
            and el.X is not None
            and not math.isnan(el.X)
        )

    def distance(el: Element) -> float:
        group_penalty = 0 if el.group == base.group else (2 if abs(el.group - base.group) <= 2 else 5)
        return abs(el.X - base.X) + abs(float(el.atomic_radius) - float(base.atomic_radius)) + group_penalty

    candidates = sorted((el for el in Element if usable(el)), key=distance)
    return [str(el) for el in candidates[:pool_size]]
