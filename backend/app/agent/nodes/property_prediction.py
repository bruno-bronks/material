from app.agent.state import MaterialState
from app.gnn.enrich import enrich_with_bulk_modulus
from app.llm.client import get_llm
from app.prompts.loader import render_prompt
from app.rag.context_builder import build_context, context_to_prompt_text
from app.tools.router import search_materials


def node_property_prediction(state: MaterialState) -> dict:
    question = state["user_question"]

    materials = search_materials(question)
    materials = enrich_with_bulk_modulus(materials)
    rag_context = build_context(question)
    context_text = context_to_prompt_text(rag_context)

    if materials:
        materials_block = "\n".join(f"- {item}" for item in materials[:10])
        context_text = (
            f"{context_text}\n\n### tools (Materials Project / OQMD / AFLOW, inclui energia de "
            f"formação e módulo de compressibilidade previstos por GNN quando disponíveis)\n"
            f"{materials_block}"
        )

    prompt = render_prompt("property_prediction.jinja2", material=question, context=context_text)
    response = get_llm().invoke(prompt)

    return {"materials": materials, "context": rag_context, "raw_answer": response.content}
