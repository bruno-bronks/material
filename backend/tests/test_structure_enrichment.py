from app.agent.nodes.structure_enrichment import node_structure_enrichment


def test_noop_without_ranking():
    assert node_structure_enrichment({"ranking": []}) == {}


def test_noop_when_top_candidate_is_not_from_materials_project():
    state = {"ranking": [{"source": "aflow", "material_name": "x"}]}
    assert node_structure_enrichment(state) == {}


def test_noop_when_material_id_missing():
    state = {"ranking": [{"source": "materials_project", "material_name": "x"}]}
    assert node_structure_enrichment(state) == {}
