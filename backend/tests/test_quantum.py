from app.agent.nodes.quantum_chemistry import _H2_PATTERN
from app.quantum.qaoa import solve_max_cut
from app.quantum.vqe import compute_ground_state_energy


def test_h2_pattern_matches_common_phrasings():
    assert _H2_PATTERN.search("qual a energia do H2")
    assert _H2_PATTERN.search("simule a molécula de hidrogênio via VQE")
    assert not _H2_PATTERN.search("qual a energia da molécula de água")


def test_compute_ground_state_energy_unsupported_molecule_returns_none():
    assert compute_ground_state_energy("h2o") is None


def test_compute_ground_state_energy_degrades_gracefully_without_quantum_libs():
    # Neste ambiente de teste (Windows/CI sem requirements-quantum.txt), qiskit/pyscf não
    # estão instalados — a função deve retornar None, nunca lançar exceção.
    result = compute_ground_state_energy("h2")
    assert result is None or result.molecule.startswith("H")


def test_solve_max_cut_default_graph_finds_known_optimum():
    # QAOA não precisa de PySCF — roda em qualquer SO, incluindo Windows/CI.
    result = solve_max_cut()
    assert result is not None
    # Grafo-ciclo de 4 nós é bipartido: o corte máximo é "todas as 4 arestas".
    assert result.exact_cut_value == 4
    assert result.qaoa_cut_value <= result.exact_cut_value
