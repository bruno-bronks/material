from app.agent.state import MaterialState
from app.tools import materials_project


def node_material_generator(state: MaterialState) -> dict:
    """V5: gera a estrutura hipotética por substituição de elemento na estrutura base.

    Não inventa geometria do zero (isso seria um modelo generativo, fora de escopo) —
    parte de uma estrutura real e aplica a substituição proposta pela hipótese.
    """
    seed_material_id = state.get("seed_material_id")
    substitution = state.get("substitution")
    if not seed_material_id or not substitution:
        return {"candidate_structure_cif": "", "candidate_composition": ""}

    structure = materials_project.get_structure(seed_material_id)
    if structure is None:
        return {"candidate_structure_cif": "", "candidate_composition": ""}

    candidate = structure.copy()
    candidate.replace_species({substitution["element_from"]: substitution["element_to"]})

    if candidate.composition.reduced_formula == structure.composition.reduced_formula:
        # element_from não existe na estrutura base — substituição não teve efeito.
        return {"candidate_structure_cif": "", "candidate_composition": ""}

    return {
        "candidate_structure_cif": candidate.to(fmt="cif"),
        "candidate_composition": candidate.composition.reduced_formula,
    }
