from functools import lru_cache

from langgraph.graph import END, StateGraph

from app.agent.nodes.aggregator import node_aggregator
from app.agent.nodes.compare_materials import node_compare_materials
from app.agent.nodes.critic import node_critic
from app.agent.nodes.explain_material import node_explain_material
from app.agent.nodes.hypothesis import node_hypothesis
from app.agent.nodes.material_generator import node_material_generator
from app.agent.nodes.material_search import node_material_search
from app.agent.nodes.paper_search import node_paper_search
from app.agent.nodes.planner import node_planner
from app.agent.nodes.property_prediction import node_property_prediction
from app.agent.nodes.ranker import node_ranker
from app.agent.nodes.reflection import node_reflection
from app.agent.nodes.report_generator import node_report_generator
from app.agent.nodes.simulation import node_simulation
from app.agent.nodes.simulation_planner import node_simulation_planner
from app.agent.state import MaterialState

SIMPLE_INTENT_NODES = {
    "material_search": "material_search",
    "compare_materials": "compare_materials",
    "explain_material": "explain_material",
    "paper_search": "paper_search",
    "simulation": "simulation",
    "property_prediction": "property_prediction",
}


def _discovery_route(state: MaterialState) -> str:
    """V5/V6 lite: aceita, esgotou iterações/pool de candidatos, ou volta pra reflexão."""
    verdict = state.get("discovery_verdict") or {}
    iteration = state.get("discovery_iteration", 0)
    max_iterations = state.get("discovery_max_iterations", 0)
    pool_exhausted = not state.get("candidate_pool")

    if verdict.get("accepted") or iteration >= max_iterations or pool_exhausted:
        return "report_generator"
    return "node_reflection"


@lru_cache
def build_graph():
    graph = StateGraph(MaterialState)

    graph.add_node("planner", node_planner)
    graph.add_node("material_search", node_material_search)
    graph.add_node("paper_search", node_paper_search)
    graph.add_node("explain_material", node_explain_material)
    graph.add_node("compare_materials", node_compare_materials)
    graph.add_node("property_prediction", node_property_prediction)
    graph.add_node("simulation", node_simulation)
    graph.add_node("ranker", node_ranker)
    graph.add_node("aggregator", node_aggregator)
    graph.add_node("report_generator", node_report_generator)

    # V5 — Scientific Agent (intenção material_discovery)
    graph.add_node("node_hypothesis", node_hypothesis)
    graph.add_node("node_material_generator", node_material_generator)
    graph.add_node("node_simulation_planner", node_simulation_planner)
    graph.add_node("node_critic", node_critic)
    graph.add_node("node_reflection", node_reflection)

    graph.set_entry_point("planner")
    graph.add_conditional_edges(
        "planner",
        lambda state: state["intent"],
        {**SIMPLE_INTENT_NODES, "material_discovery": "node_hypothesis"},
    )

    for intent_node in SIMPLE_INTENT_NODES.values():
        graph.add_edge(intent_node, "ranker")

    graph.add_edge("ranker", "aggregator")
    graph.add_edge("aggregator", "report_generator")

    # Loop V5: hypothesis -> generator -> simulation_planner -> critic -> (reflection -> generator) | report
    graph.add_edge("node_hypothesis", "node_material_generator")
    graph.add_edge("node_material_generator", "node_simulation_planner")
    graph.add_edge("node_simulation_planner", "node_critic")
    graph.add_conditional_edges(
        "node_critic",
        _discovery_route,
        {"report_generator": "report_generator", "node_reflection": "node_reflection"},
    )
    graph.add_edge("node_reflection", "node_material_generator")

    graph.add_edge("report_generator", END)

    return graph.compile()
