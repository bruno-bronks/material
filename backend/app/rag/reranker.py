def rerank_by_keyword_overlap(question: str, hits: list[dict]) -> list[dict]:
    """Re-ranking leve por overlap de termos.

    Placeholder local e gratuito para os modelos citados no Context_Engineering.md
    (Cohere Rerank / BGE Reranker / Cross Encoder), que podem ser plugados aqui
    no lugar desta heurística quando houver orçamento para um modelo dedicado.
    """
    question_terms = {term for term in question.lower().split() if len(term) > 2}

    def score(hit: dict) -> tuple[int, float]:
        doc_terms = set(hit["document"].lower().split())
        overlap = len(question_terms & doc_terms)
        return (-overlap, hit["distance"])

    return sorted(hits, key=score)
