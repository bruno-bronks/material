import uuid

from app.ingestion.enrich import enrich_content
from app.rag import vectorstore
from app.rag.chunking import chunk_text
from app.schemas.enrichment import ContentEnrichment
from app.tools.router import search_materials, search_papers


def ingest_papers(query: str, limit: int = 10) -> int:
    """Pipeline ETL: Extract (tools) -> Transform (texto) -> Enrich (keywords/aplicação/resumo
    via LLM) -> Store (Chroma: chunks em 'papers', resumo em 'summaries')."""
    papers = search_papers(query, limit=limit)

    count = 0
    for paper in papers:
        text = _paper_to_text(paper)
        if not text.strip():
            continue

        enrichment = enrich_content(text)
        metadata = _paper_metadata(paper, enrichment)

        for chunk in chunk_text(text, kind="paper"):
            vectorstore.add_documents(
                "papers", ids=[str(uuid.uuid4())], documents=[chunk], metadatas=[metadata]
            )
            count += 1

        _store_summary(enrichment, metadata)
    return count


def ingest_materials(query: str, limit: int = 10) -> int:
    materials = search_materials(query, limit=limit)

    count = 0
    for material in materials:
        text = _material_to_text(material)
        if not text.strip():
            continue

        enrichment = enrich_content(text)
        metadata = _material_metadata(material, enrichment)

        for chunk in chunk_text(text, kind="material"):
            vectorstore.add_documents(
                "materials", ids=[str(uuid.uuid4())], documents=[chunk], metadatas=[metadata]
            )
            count += 1

        _store_summary(enrichment, metadata)
    return count


def _store_summary(enrichment: ContentEnrichment | None, metadata: dict) -> None:
    if enrichment is None or not enrichment.summary.strip():
        return
    for chunk in chunk_text(enrichment.summary, kind="summary"):
        vectorstore.add_documents(
            "summaries", ids=[str(uuid.uuid4())], documents=[chunk], metadatas=[metadata]
        )


def _paper_to_text(paper: dict) -> str:
    parts = [paper.get("title") or "", paper.get("abstract") or ""]
    return "\n".join(part for part in parts if part)


def _paper_metadata(paper: dict, enrichment: ContentEnrichment | None) -> dict:
    return {
        "source": paper.get("source") or "",
        "doi": paper.get("doi") or "",
        "year": str(paper.get("year") or ""),
        "authors": ", ".join(paper.get("authors") or [])[:500],
        "application": enrichment.application if enrichment else "",
        "keywords": ", ".join(enrichment.keywords) if enrichment else "",
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


def _material_metadata(material: dict, enrichment: ContentEnrichment | None) -> dict:
    return {
        "source": material.get("source") or "",
        "material": material.get("material_name") or "",
        "application": enrichment.application if enrichment else "",
        "keywords": ", ".join(enrichment.keywords) if enrichment else "",
    }
