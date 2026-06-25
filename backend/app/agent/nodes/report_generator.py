import json

from app.agent.state import MaterialState
from app.llm.client import get_llm
from app.prompts.loader import render_prompt


def node_report_generator(state: MaterialState) -> dict:
    prompt = render_prompt(
        "report_generator.jinja2",
        question=state["user_question"],
        intent=state.get("intent", ""),
        materials=_to_json(state.get("materials", [])),
        papers=_to_json(state.get("papers", [])),
        simulations=_to_json(state.get("simulations", [])),
        ranking=_to_json(state.get("ranking", [])),
        discovery_log=_to_json(state.get("discovery_log", [])),
        discovery_verdict=_to_json(state.get("discovery_verdict", {})),
    )
    full_prompt = (
        f"{prompt}\n\nResposta preliminar do especialista de domínio "
        f"(use como base, mas siga o formato pedido acima):\n{state.get('raw_answer', '')}"
    )

    response = get_llm().invoke(full_prompt)
    return {"report": response.content}


def _to_json(data) -> str:
    return json.dumps(data, ensure_ascii=False, default=str)[:4000]
