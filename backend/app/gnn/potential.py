from functools import lru_cache

PES_MODEL = "M3GNet-PES-MatPES-PBE-2025.2"


@lru_cache
def get_m3gnet_potential():
    """Potencial interatômico universal compartilhado por elastic.py (V3) e simulation/relax.py (V4)."""
    import matgl

    return matgl.load_model(PES_MODEL)
