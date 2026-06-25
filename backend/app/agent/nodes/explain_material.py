from app.agent.state import MaterialState
from app.llm.client import get_llm
from app.prompts.loader import render_prompt
from app.rag.context_builder import build_context, context_to_prompt_text
from app.tools.router import search_materials, search_papers


def node_explain_material(state: MaterialState) -> dict:
    question = state["user_question"]

    materials = search_materials(question)
    papers = search_papers(question, limit=3)
    rag_context = build_context(question)
    context_text = context_to_prompt_text(rag_context)

    prompt = render_prompt("explain_material.jinja2", material=question, context=context_text)
    response = get_llm().invoke(prompt)

    return {
        "materials": materials,
        "papers": papers,
        "context": rag_context,
        "raw_answer": response.content,
    }
