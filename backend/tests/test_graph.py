from app.agent.graph import build_graph


def test_graph_builds_without_error():
    graph = build_graph()
    assert graph is not None


def test_graph_is_cached():
    assert build_graph() is build_graph()
