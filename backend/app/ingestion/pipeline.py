import uuid

from app.rag import vectorstore
from app.rag.chunking import chunk_text
from app.tools.router import search_materials, search_papers


def ingest_papers(query: str, limit: int = 10) -> int:
    """Pipeline ETL: Extract (tools) -> Transform/Validate (texto) -> Enrich (metadata) -> Store (Chroma)."""
    papers = search_papers(query, limit=limit)

    count = 0
    for paper in papers:
        text = _paper_to_text(paper)
        if not text.strip():
            continue
        for chunk in chunk_text(text, kind="paper"):
            vectorstore.add_documents(
                "papers",
                ids=[str(uuid.uuid4())],
                documents=[chunk],
                metadatas=[_paper_metadata(paper)],
            )
            count += 1
    return count


def ingest_materials(query: str, limit: int = 10) -> int:
    materials = search_materials(query, limit=limit)

    count = 0
    for material in materials:
        text = _material_to_text(material)
        if not text.strip():
            continue
        for chunk in chunk_text(text, kind="material"):
            vectorstore.add_documents(
                "materials",
                ids=[str(uuid.uuid4())],
                documents=[chunk],
                metadatas=[_material_metadata(material)],
            )
            count += 1
    return count


def _paper_to_text(paper: dict) -> str:
    parts = [paper.get("title") or "", paper.get("abstract") or ""]
    return "\n".join(part for part in parts if part)


def _paper_metadata(paper: dict) -> dict:
    return {
        "source": paper.get("source") or "",
        "doi": paper.get("doi") or "",
        "year": str(paper.get("year") or ""),
        "authors": ", ".join(paper.get("authors") or [])[:500],
    }


def _material_to_text(material: dict) -> str:
    parts = [
        f"material: {material.get('material_name') or ''}",
        f"composição: {material.get('composition') or ''}",
        f"densidade: {material.get('density') or ''}",
        f"band_gap: {material.get('band_gap') or ''}",
        f"estrutura cristalina: {material.get('crystal_structure') or ''}",
        f"fonte: {material.get('source') or ''}",
    ]
    return "\n".join(parts)


def _material_metadata(material: dict) -> dict:
    return {
        "source": material.get("source") or "",
        "material": material.get("material_name") or "",
    }
