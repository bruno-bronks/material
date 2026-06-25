import pytest
from pymatgen.core import Lattice, Structure

from app.gnn.predictor import predict_band_gap, predict_formation_energy

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def nacl_structure():
    return Structure.from_spacegroup("Fm-3m", Lattice.cubic(5.69), ["Na", "Cl"], [[0, 0, 0], [0.5, 0.5, 0.5]])


def test_formation_energy_plausible_for_nacl(nacl_structure):
    energy = predict_formation_energy(nacl_structure)
    assert energy is not None
    # NaCl é um composto estável; energia de formação negativa esperada, ordem de -1 a -5 eV/átomo.
    assert -5 < energy < 0


def test_band_gap_predicts_wide_gap_insulator_for_nacl(nacl_structure):
    # NaCl é um isolante de gap largo (~8.5 eV experimental); GLLB-SC deve prever algo bem
    # acima de zero, bem distante do regime metálico.
    gap = predict_band_gap(nacl_structure, fidelity="gllb-sc")
    assert gap is not None
    assert gap > 3


def test_band_gap_never_negative(nacl_structure):
    for fidelity in ("pbe", "gllb-sc", "hse", "scan"):
        gap = predict_band_gap(nacl_structure, fidelity=fidelity)
        assert gap is not None
        assert gap >= 0
