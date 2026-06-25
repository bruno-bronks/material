from app.agent.state import MaterialState
from app.llm.client import get_llm
from app.prompts.loader import render_prompt
from app.schemas.discovery import CriticVerdict

MAX_ACCEPTABLE_FORCE_EV_A = 0.5


def node_critic(state: MaterialState) -> dict:
    """V5: aplica critérios físicos objetivos e, se passar, julgamento do LLM contra o objetivo."""
    metrics = state.get("discovery_metrics") or {}
    substitution = state.get("substitution") or {}

    verdict = _hard_gate(metrics)
    if verdict is None:
        prompt = render_prompt(
            "discovery_critic.jinja2",
            objective=state["user_question"],
            element_from=substitution.get("element_from"),
            element_to=substitution.get("element_to"),
            candidate_composition=state.get("candidate_composition"),
            metrics=metrics,
        )
        verdict = get_llm().with_structured_output(CriticVerdict).invoke(prompt).model_dump()

    log_entry = {
        "iteration": state.get("discovery_iteration"),
        "substitution": substitution,
        "candidate_composition": state.get("candidate_composition"),
        "metrics": metrics,
        "verdict": verdict,
    }

    return {
        "discovery_verdict": verdict,
        "discovery_log": (state.get("discovery_log") or []) + [log_entry],
    }


def _hard_gate(metrics: dict) -> dict | None:
    """Critérios físicos que não dependem de julgamento do LLM. None = passou, segue pro LLM."""
    if not metrics:
        return {
            "accepted": False,
            "reasons": ["Não foi possível gerar/simular um candidato válido para esta substituição."],
        }

    if not metrics.get("relax_converged", False):
        return {
            "accepted": False,
            "reasons": ["A relaxação estrutural não convergiu — candidato instável ou simulação inviável."],
        }

    max_force = metrics.get("relax_max_force_ev_a", 0)
    if max_force > MAX_ACCEPTABLE_FORCE_EV_A:
        return {
            "accepted": False,
            "reasons": [f"Força residual após relaxação ({max_force:.3f} eV/Å) acima do aceitável."],
        }

    return None
