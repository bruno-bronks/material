from app.agent.state import MaterialState
from app.tools import materials_project


def node_structure_enrichment(state: MaterialState) -> dict:
    """Busca a estrutura cristalina completa (CIF) do candidato top-ranqueado, pro visualizador
    3D do frontend. Só o Materials Project retorna posições atômicas/parâmetros de rede
    completos hoje — OQMD e AFLOW (neste projeto) só têm metadados agregados, sem coordenadas,
    então o no-op abaixo é o caminho esperado pra esses casos (não é um bug).
    """
    ranking = state.get("ranking") or []
    if not ranking:
        return {}

    top = ranking[0]
    if top.get("source") != "materials_project" or not top.get("material_id"):
        return {}

    structure = materials_project.get_structure(top["material_id"])
    if structure is None:
        return {}

    return {"candidate_structure_cif": structure.to(fmt="cif")}
