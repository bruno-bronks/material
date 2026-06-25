import re

from app.agent.state import MaterialState
from app.llm.client import get_llm
from app.prompts.loader import render_prompt
from app.quantum.vqe import compute_ground_state_energy

_H2_PATTERN = re.compile(r"\bh2\b|\bh₂\b|hidrogênio molecular|molécula de hidrogênio", re.IGNORECASE)


def node_quantum_chemistry(state: MaterialState) -> dict:
    """Quantum Research Assistant (escopo restrito): VQE real só pra H2 — ver app/quantum/vqe.py
    pra explicação completa do porquê do escopo (água precisaria de 92 parâmetros de ansatz e
    não converge em tempo de chat)."""
    question = state["user_question"]

    if not _H2_PATTERN.search(question):
        raw_answer = (
            "Hoje o cálculo real de energia via VQE (Variational Quantum Eigensolver) só está "
            "disponível para a molécula de H2 (hidrogênio molecular). Moléculas maiores, como "
            "água, exigem um circuito quântico grande demais para convergir em tempo de chat "
            "(testamos: 92 parâmetros no ansatz, não converge em minutos num simulador "
            "clássico). Pergunte sobre H2 para ver o cálculo quântico real em ação."
        )
        return {"raw_answer": raw_answer}

    result = compute_ground_state_energy("h2")

    if result is None:
        raw_answer = (
            "O cálculo de VQE depende de bibliotecas (Qiskit, Qiskit Nature, PySCF) que não "
            "estão instaladas/disponíveis neste ambiente — o PySCF, em particular, não tem "
            "suporte ao Windows. Essa funcionalidade só roda no servidor de produção (Linux)."
        )
        return {"raw_answer": raw_answer}

    prompt = render_prompt(
        "quantum_chemistry.jinja2",
        question=question,
        molecule=result.molecule,
        num_qubits=result.num_qubits,
        hf_energy=result.hartree_fock_energy,
        vqe_energy=result.vqe_energy,
        exact_energy=result.exact_energy,
        error=result.vqe_error_hartree,
    )
    response = get_llm().invoke(prompt)

    return {"raw_answer": response.content}
