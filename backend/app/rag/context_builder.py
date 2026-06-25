from app.rag import vectorstore
from app.rag.reranker import rerank_by_keyword_overlap

RAG_TYPES = ("materials", "papers", "summaries")


def build_context(question: str, n_results: int = 4) -> dict[str, list[dict]]:
    """Question -> Material RAG -> Paper RAG -> (Graph RAG) -> Merge -> Re-ranking."""
    context = {kind: vectorstore.query(kind, question, n_results=n_results) for kind in RAG_TYPES}
    return {kind: rerank_by_keyword_overlap(question, hits) for kind, hits in context.items()}


def context_to_prompt_text(context: dict[str, list[dict]]) -> str:
    sections = []
    for kind, hits in context.items():
        if not hits:
            continue
        block = "\n".join(f"- {hit['document'][:500]}" for hit in hits)
        sections.append(f"### {kind}\n{block}")

    if not sections:
        return "(base de conhecimento vetorial ainda vazia para esta consulta — use apenas os resultados das tools/APIs abaixo)"
    return "\n\n".join(sections)
