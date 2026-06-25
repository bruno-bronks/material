import re

from app.agent.state import MaterialState
from app.llm.client import get_llm
from app.prompts.loader import render_prompt
from app.rag.context_builder import build_context, context_to_prompt_text
from app.tools.router import search_materials

_SPLIT_PATTERN = re.compile(r"\bvs\.?\b|\bversus\b|\bcontra\b", re.IGNORECASE)


def node_compare_materials(state: MaterialState) -> dict:
    question = state["user_question"]
    material_1, material_2 = _split_materials(question)

    rag_context = build_context(question)
    context_text = context_to_prompt_text(rag_context)

    tool_results = search_materials(material_1)
    if material_2:
        tool_results += search_materials(material_2)

    prompt = render_prompt(
        "compare_materials.jinja2",
        material_1=material_1,
        material_2=material_2 or "(segundo material não identificado claramente na pergunta)",
        context=context_text,
    )
    response = get_llm().invoke(prompt)

    return {"materials": tool_results, "context": rag_context, "raw_answer": response.content}


def _split_materials(question: str) -> tuple[str, str]:
    parts = _SPLIT_PATTERN.split(question, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return question, ""
