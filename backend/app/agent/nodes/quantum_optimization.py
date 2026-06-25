from app.agent.state import MaterialState
from app.llm.client import get_llm
from app.prompts.loader import render_prompt
from app.quantum.qaoa import solve_max_cut


def node_quantum_optimization(state: MaterialState) -> dict:
    """Quantum Research Assistant — Agente 6 (Quantum Algorithm Agent), escopo QAOA/Max-Cut.

    Sem PySCF (diferente do node_quantum_chemistry) — roda em qualquer SO. Escopo restrito a
    um grafo de demonstração fixo (ver app/quantum/qaoa.py), pelo mesmo motivo do V5/V6 e do
    quantum_chemistry: não dá pra extrair um grafo arbitrário de texto livre sem risco real de
    inventar uma estrutura de problema que o usuário não pediu.
    """
    question = state["user_question"]

    result = solve_max_cut()

    if result is None:
        raw_answer = (
            "O cálculo de QAOA depende de bibliotecas (Qiskit, Qiskit Algorithms) que não "
            "estão instaladas/disponíveis neste ambiente."
        )
        return {"raw_answer": raw_answer}

    prompt = render_prompt(
        "quantum_optimization.jinja2",
        question=question,
        graph_label=result.graph_label,
        num_nodes=result.num_nodes,
        num_edges=result.num_edges,
        partition=result.qaoa_partition,
        qaoa_cut_value=result.qaoa_cut_value,
        exact_cut_value=result.exact_cut_value,
        matched_exact=result.matched_exact,
    )
    response = get_llm().invoke(prompt)

    return {"raw_answer": response.content}
