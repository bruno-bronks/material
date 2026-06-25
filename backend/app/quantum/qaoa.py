"""QAOA real (Quantum Approximate Optimization Algorithm) para Max-Cut, via Qiskit.

Diferente do VQE (vqe.py): não depende de PySCF, então roda em qualquer sistema operacional —
testado e funcionando neste Windows local, sem precisar da VPS.

Max-Cut: particionar os nós de um grafo em 2 grupos maximizando o número de arestas entre os
grupos. Problema NP-difícil clássico, o exemplo padrão de "Problemas de Otimização" do
Quantum_Research_Assistant.md. Escopo restrito a um grafo pequeno (mesma cautela do vqe.py: só
o que dá pra verificar e rodar rápido), com a solução exata calculada por força bruta (viável
até ~15 nós) como gabarito.
"""

from dataclasses import dataclass
from itertools import product

DEFAULT_GRAPH_EDGES = [(0, 1), (1, 2), (2, 3), (3, 0)]
DEFAULT_GRAPH_LABEL = "grafo-ciclo de 4 nós (0-1-2-3-0)"
MAX_NODES = 12  # guard de custo: força bruta exata + QAOA ficam caros acima disso


@dataclass
class QAOAResult:
    graph_label: str
    num_nodes: int
    num_edges: int
    qaoa_partition: str
    qaoa_cut_value: int
    exact_cut_value: int
    matched_exact: bool


def _cut_value(bitstring: str, edges: list[tuple[int, int]]) -> int:
    return sum(1 for i, j in edges if bitstring[i] != bitstring[j])


def _exact_max_cut(num_nodes: int, edges: list[tuple[int, int]]) -> int:
    return max(_cut_value("".join(bits), edges) for bits in product("01", repeat=num_nodes))


def solve_max_cut(
    edges: list[tuple[int, int]] | None = None, label: str | None = None
) -> QAOAResult | None:
    edges = edges or DEFAULT_GRAPH_EDGES
    label = label or DEFAULT_GRAPH_LABEL
    num_nodes = max(max(edge) for edge in edges) + 1

    if num_nodes > MAX_NODES:
        return None

    try:
        from qiskit.primitives import StatevectorSampler
        from qiskit.quantum_info import SparsePauliOp
        from qiskit_algorithms import QAOA
        from qiskit_algorithms.optimizers import COBYLA
    except ImportError:
        return None

    try:
        pauli_terms = []
        for i, j in edges:
            z_string = ["I"] * num_nodes
            z_string[i] = "Z"
            z_string[j] = "Z"
            pauli_terms.append(("".join(z_string), 1.0))
        cost_hamiltonian = SparsePauliOp.from_list(pauli_terms)

        qaoa = QAOA(sampler=StatevectorSampler(), optimizer=COBYLA(), reps=2)
        result = qaoa.compute_minimum_eigenvalue(cost_hamiltonian)

        bitstring = result.best_measurement["bitstring"]
        qaoa_cut = _cut_value(bitstring, edges)
        exact_cut = _exact_max_cut(num_nodes, edges)
    except Exception:
        return None

    return QAOAResult(
        graph_label=label,
        num_nodes=num_nodes,
        num_edges=len(edges),
        qaoa_partition=bitstring,
        qaoa_cut_value=qaoa_cut,
        exact_cut_value=exact_cut,
        matched_exact=qaoa_cut == exact_cut,
    )
