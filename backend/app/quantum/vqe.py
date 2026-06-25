"""VQE real (Variational Quantum Eigensolver) via Qiskit + Qiskit Nature + PySCF.

Diferente do resto do projeto (V2-V6): isso não é aproximação por modelo de ML, é uma
simulação clássica de um circuito quântico de verdade. Só roda em Linux/Mac — ver
requirements-quantum.txt. Sem essas libs instaladas, retorna None (graceful).

Escopo deliberadamente restrito a H2: testamos H2O (o exemplo principal do documento
Quantum_Research_Assistant.md) e mesmo com FreezeCoreTransformer (orbitais internos
congelados) o problema tem 12 qubits / 92 parâmetros no ansatz UCCSD — não converge em
minutos num simulador clássico, então não cabe num tempo de resposta de chat. H2 tem só
4 qubits / 3 parâmetros e resolve em <1s com precisão essencialmente exata.
"""

from dataclasses import dataclass

# Geometria do H2: 0.735 Å é o valor DEFAULT do próprio PySCFDriver do qiskit-nature
# (não é um número que escolhemos — é o canônico da biblioteca, verificado via
# inspect.signature(PySCFDriver.__init__)).
SUPPORTED_MOLECULES = {
    "h2": {
        "atom": "H 0.0 0.0 0.0; H 0.0 0.0 0.735",
        "label": "H₂ (hidrogênio molecular, 0.735 Å)",
    },
}

MAX_ANSATZ_PARAMETERS = 20  # guard de custo — ver docstring do módulo (H2O tem 92)


@dataclass
class VQEResult:
    molecule: str
    basis: str
    num_qubits: int
    hartree_fock_energy: float
    vqe_energy: float
    exact_energy: float
    vqe_error_hartree: float


def compute_ground_state_energy(molecule_key: str, basis: str = "sto3g") -> VQEResult | None:
    spec = SUPPORTED_MOLECULES.get(molecule_key)
    if spec is None:
        return None

    try:
        from pyscf import fci, gto, scf
        from qiskit.primitives import StatevectorEstimator
        from qiskit_algorithms import VQE
        from qiskit_algorithms.optimizers import SLSQP
        from qiskit_nature.second_q.algorithms import GroundStateEigensolver
        from qiskit_nature.second_q.circuit.library import UCCSD, HartreeFock
        from qiskit_nature.second_q.drivers import PySCFDriver
        from qiskit_nature.second_q.mappers import JordanWignerMapper
    except ImportError:
        return None

    try:
        driver = PySCFDriver(atom=spec["atom"], basis=basis)
        problem = driver.run()

        mapper = JordanWignerMapper()
        ansatz = UCCSD(
            problem.num_spatial_orbitals,
            problem.num_particles,
            mapper,
            initial_state=HartreeFock(problem.num_spatial_orbitals, problem.num_particles, mapper),
        )

        if ansatz.num_parameters > MAX_ANSATZ_PARAMETERS:
            return None

        vqe_solver = VQE(StatevectorEstimator(), ansatz, SLSQP())
        vqe_solver.initial_point = [0.0] * ansatz.num_parameters
        solver = GroundStateEigensolver(mapper, vqe_solver)
        result = solver.solve(problem)
        vqe_energy = float(result.total_energies[0])

        # Referência exata (FCI), calculada classicamente com o PySCF puro — só é viável
        # pra sistemas deste tamanho, mas serve de "gabarito" pra avaliar o VQE.
        mol = gto.M(atom=spec["atom"], basis=basis)
        mf = scf.RHF(mol).run(verbose=0)
        exact_energy = float(fci.FCI(mf).kernel()[0])
    except Exception:
        return None

    return VQEResult(
        molecule=spec["label"],
        basis=basis,
        num_qubits=2 * problem.num_spatial_orbitals,
        hartree_fock_energy=float(problem.reference_energy),
        vqe_energy=vqe_energy,
        exact_energy=exact_energy,
        vqe_error_hartree=abs(vqe_energy - exact_energy),
    )
