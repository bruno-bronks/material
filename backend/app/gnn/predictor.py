from functools import lru_cache

from pymatgen.core import Structure

FORMATION_ENERGY_MODEL = "MEGNet-Eform-MP-2018.6.1"
BAND_GAP_MODEL = "MEGNet-BandGap-mfi-MP-2019.4.1"

# O checkpoint de band gap é multi-fidelidade: precisa de um state_attr indicando o
# método (não um valor contínuo). É um índice de classe (LongTensor), não one-hot —
# a camada de embedding interna (`layer_state_embedding`) é um torch.nn.Embedding(4, 16).
BAND_GAP_FIDELITY = {"pbe": 0, "gllb-sc": 1, "hse": 2, "scan": 3}


@lru_cache
def _formation_energy_model():
    import matgl

    return matgl.load_model(FORMATION_ENERGY_MODEL)


@lru_cache
def _band_gap_model():
    import matgl

    return matgl.load_model(BAND_GAP_MODEL)


def predict_formation_energy(structure: Structure) -> float | None:
    """Energia de formação prevista (eV/átomo) via MEGNet pré-treinado."""
    try:
        prediction = _formation_energy_model().predict_structure(structure)
        return float(prediction)
    except Exception:
        return None


def predict_band_gap(structure: Structure, fidelity: str = "pbe") -> float | None:
    """Band gap previsto (eV) via MEGNet multi-fidelidade pré-treinado.

    `fidelity` = "pbe" (padrão, mesma convenção do `band_gap` que já vem do
    Materials Project/OQMD/AFLOW) | "gllb-sc" | "hse" | "scan" — o modelo foi
    treinado para aproximar cada um desses métodos separadamente.
    """
    import torch

    try:
        state_attr = torch.tensor([BAND_GAP_FIDELITY[fidelity]], dtype=torch.long)
        prediction = _band_gap_model().predict_structure(structure, state_attr=state_attr)
        return max(0.0, float(prediction))
    except Exception:
        return None
