from app.agent.state import MaterialState
from app.llm.client import get_llm
from app.prompts.loader import render_prompt
from app.rag.context_builder import build_context, context_to_prompt_text
from app.tools.router import search_materials


def node_material_search(state: MaterialState) -> dict:
    question = state["user_question"]

    tool_results = search_materials(question)
    rag_context = build_context(question)
    context_text = _merge_context(rag_context, tool_results)

    prompt = render_prompt(
        "material_search.jinja2",
        objective=question,
        constraints=state.get("constraints") or "(nenhuma restrição explícita identificada)",
        context=context_text,
    )
    response = get_llm().invoke(prompt)

    return {
        "materials": tool_results,
        "candidates": tool_results,
        "context": rag_context,
        "raw_answer": response.content,
    }


def _merge_context(rag_context: dict, tool_results: list[dict]) -> str:
    context_text = context_to_prompt_text(rag_context)
    if not tool_results:
        return context_text

    tool_block = "\n".join(f"- {item}" for item in tool_results[:10])
    return f"{context_text}\n\n### tools (Materials Project / OQMD / AFLOW)\n{tool_block}"
