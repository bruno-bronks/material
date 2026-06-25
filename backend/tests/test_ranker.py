from app.agent.nodes.ranker import node_ranker


def test_ranker_prefers_real_stability_data_over_gnn_prediction():
    state = {
        "materials": [
            {"material_name": "no_data", "density": 5.0},
            {"material_name": "aflow_real", "source": "aflow", "formation_energy": -0.5, "density": 6.0},
            {"material_name": "mp_real", "source": "materials_project", "energy_above_hull": 0.05, "density": 4.0},
            {"material_name": "gnn_only", "gnn_formation_energy_ev_atom": -0.1, "density": 3.0},
        ]
    }

    ranking = node_ranker(state)["ranking"]
    names = [m["material_name"] for m in ranking]

    assert names == ["mp_real", "gnn_only", "aflow_real", "no_data"]


def test_ranker_handles_empty_materials():
    assert node_ranker({"materials": []})["ranking"] == []


def test_ranker_limits_to_five():
    materials = [{"material_name": f"m{i}", "energy_above_hull": i * 0.01} for i in range(10)]
    ranking = node_ranker({"materials": materials})["ranking"]
    assert len(ranking) == 5
