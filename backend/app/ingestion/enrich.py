from app.llm.client import get_llm
from app.prompts.loader import render_prompt
from app.schemas.enrichment import APPLICATION_CATEGORIES, ContentEnrichment


def enrich_content(text: str) -> ContentEnrichment | None:
    """"Enrich" real do pipeline ETL (Context_Engineering.md: Extract → Transform → Validate →
    Enrich → Store). Extrai keywords e classifica aplicação a partir do texto de verdade (não
    inventa `temperature_range` — não temos como confirmar isso a partir do abstract/dado da
    tool sem risco real de alucinação, por isso esse campo do schema do doc fica de fora).
    """
    if not text.strip():
        return None

    prompt = render_prompt(
        "enrich_content.jinja2",
        content=text[:3000],
        categories=", ".join(APPLICATION_CATEGORIES),
    )
    try:
        return get_llm(temperature=0).with_structured_output(ContentEnrichment).invoke(prompt)
    except Exception:
        return None
