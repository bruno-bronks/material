from app.agent.state import MaterialState
from app.llm.client import get_llm
from app.prompts.loader import render_prompt

VALID_INTENTS = {
    "material_search",
    "compare_materials",
    "explain_material",
    "paper_search",
    "simulation",
    "property_prediction",
    "material_discovery",
}


def node_planner(state: MaterialState) -> dict:
    prompt = render_prompt("planner.jinja2", question=state["user_question"])
    response = get_llm(temperature=0).invoke(prompt)
    intent = response.content.strip().lower()

    if intent not in VALID_INTENTS:
        intent = "material_search"

    return {"intent": intent}
