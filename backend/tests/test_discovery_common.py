from app.agent.nodes.discovery_common import _chemically_similar_elements


def test_similar_elements_for_gold_includes_known_coinage_metals():
    candidates = _chemically_similar_elements("Au", pool_size=10)
    # Cu, Ag, Pt, Pd são quimicamente os mais próximos do Au na vida real
    # (grupo 10/11, eletronegatividade e raio atômico parecidos).
    assert {"Cu", "Ag"}.issubset(set(candidates))


def test_similar_elements_excludes_noble_gases_and_radioactive():
    candidates = _chemically_similar_elements("Au", pool_size=30)
    assert "He" not in candidates
    assert "Ne" not in candidates
    assert "Ar" not in candidates
    assert "Rn" not in candidates


def test_similar_elements_never_includes_the_base_element():
    candidates = _chemically_similar_elements("Au", pool_size=30)
    assert "Au" not in candidates


def test_similar_elements_respects_pool_size():
    candidates = _chemically_similar_elements("Si", pool_size=3)
    assert len(candidates) == 3
