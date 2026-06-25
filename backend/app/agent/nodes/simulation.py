from app.agent.state import MaterialState
from app.llm.client import get_llm
from app.prompts.loader import render_prompt
from app.simulation.relax import relax_structure
from app.tools import materials_project
from app.tools.router import search_materials

SIMULATION_METHODS = ("DFT", "Molecular Dynamics", "Monte Carlo", "Ab Initio")


def node_simulation(state: MaterialState) -> dict:
    question = state["user_question"]

    prompt = render_prompt("simulation.jinja2", material=question, objective=question)
    response = get_llm().invoke(prompt)

    mentioned = response.content.lower()
    simulations = [{"method": method} for method in SIMULATION_METHODS if method.lower() in mentioned]

    relaxation = _run_relaxation(question)
    if relaxation is not None:
        simulations.append(relaxation)

    return {"simulations": simulations, "raw_answer": response.content}


def _run_relaxation(question: str) -> dict | None:
    """V4: roda de fato uma relaxação estrutural (M3GNet) para o primeiro
    candidato do Materials Project encontrado, em vez de só sugerir o método."""
    materials = search_materials(question)
    candidate = next(
        (m for m in materials if m.get("source") == "materials_project" and m.get("material_id")),
        None,
    )
    if candidate is None:
        return None

    structure = materials_project.get_structure(candidate["material_id"])
    if structure is None:
        return None

    result = relax_structure(structure)
    if result is None:
        return None

    return {
        "method": "Relaxação estrutural (M3GNet, substituto rápido de DFT)",
        "material": candidate.get("material_name"),
        "material_id": candidate["material_id"],
        "converged": result.converged,
        "steps": result.steps,
        "initial_energy_ev_atom": result.initial_energy_ev_atom,
        "final_energy_ev_atom": result.final_energy_ev_atom,
        "max_force_ev_a": result.max_force_ev_a,
        "volume_change_pct": result.volume_change_pct,
    }
