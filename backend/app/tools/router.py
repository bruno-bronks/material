from app.gnn.enrich import enrich_with_gnn
from app.tools import aflow, arxiv, crossref, materials_project, oqmd, pubchem, semantic_scholar
from app.tools.elements import extract_elements, extract_formula


def search_materials(question: str, limit: int = 5) -> list[dict]:
    """Tool Router para a intenção material_search: Materials Project + OQMD + AFLOW."""
    elements = extract_elements(question)
    formula = extract_formula(question) or ("".join(elements) if elements else None)

    results: list[dict] = []
    if formula:
        results.extend(materials_project.search_by_formula(formula, limit=limit))
        results.extend(oqmd.search_by_composition(formula, limit=limit))
    if elements:
        results.extend(aflow.search_by_species(elements, limit=limit))
    if not results:
        results.extend(pubchem.search_by_name(question))

    return enrich_with_gnn(results)


def search_papers(question: str, limit: int = 5) -> list[dict]:
    """Tool Router para a intenção paper_search: Semantic Scholar + Crossref + arXiv."""
    results: list[dict] = []
    results.extend(semantic_scholar.search_papers(question, limit=limit))
    results.extend(crossref.search_works(question, limit=limit))
    results.extend(arxiv.search_papers(question, limit=limit))
    return results
