from app.agent.state import MaterialState


def node_aggregator(state: MaterialState) -> dict:
    """Combina materiais, artigos, contexto e previsões, removendo duplicatas."""
    materials = _dedup(state.get("materials") or [], "material_name")
    papers = _dedup(state.get("papers") or [], "doi")

    return {"materials": materials[:10], "papers": papers[:10]}


def _dedup(items: list[dict], key: str) -> list[dict]:
    seen = set()
    unique = []
    for item in items:
        value = item.get(key)
        if value:
            if value in seen:
                continue
            seen.add(value)
        unique.append(item)
    return unique
