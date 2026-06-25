import pytest


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_without_openai_key_returns_503(client, monkeypatch):
    from app.config import get_settings

    get_settings.cache_clear()
    monkeypatch.setenv("OPENAI_API_KEY", "")
    get_settings.cache_clear()

    response = client.post("/api/chat", json={"question": "titânio para turbina"})

    assert response.status_code == 503
    assert "OPENAI_API_KEY" in response.json()["detail"]

    get_settings.cache_clear()


@pytest.mark.network
@pytest.mark.slow
def test_ingest_materials(client):
    response = client.post(
        "/api/ingest",
        json={"query": "titânio liga aeroespacial", "kind": "materials", "limit": 2},
    )
    assert response.status_code == 200
    assert "materials_indexed" in response.json()


@pytest.mark.network
@pytest.mark.slow
def test_chat_material_search_end_to_end(client):
    from app.config import get_settings

    settings = get_settings()
    if not settings.openai_api_key:
        pytest.skip("requer OPENAI_API_KEY configurada em backend/.env")

    response = client.post("/api/chat", json={"question": "titânio para turbina"})

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "material_search"
    assert data["report"]
