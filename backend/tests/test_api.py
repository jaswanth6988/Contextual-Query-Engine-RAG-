import pytest
from fastapi.testclient import TestClient
from test_pipeline import FakeLLM, TestEmbeddings, pdf

from src.api import app, get_engine
from src.config import Settings
from src.engine import Engine


@pytest.fixture
def client(tmp_path):
    engine = Engine(Settings(data_dir=str(tmp_path)), TestEmbeddings(), FakeLLM())
    app.dependency_overrides[get_engine] = lambda: engine
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_http_upload_query_delete(client):
    assert client.get("/api/health").json() == {"status": "ok"}
    response = client.post(
        "/api/documents",
        files={"file": ("science.pdf", pdf("The planet follows an orbit."), "application/pdf")},
    )
    assert response.status_code == 200
    assert response.json()["chunks"] == 1
    document_id = client.get("/api/documents").json()[0]["id"]
    for mode in ["search", "ask", "agent"]:
        response = client.post(
            "/api/query",
            json={"question": "planet orbit", "mode": mode, "document_id": document_id},
        )
        assert response.status_code == 200
        assert response.json()["sources"][0]["page"] == 1
    assert client.delete(f"/api/documents/{document_id}").status_code == 204
    assert client.get("/api/documents").json() == []
    assert client.delete(f"/api/documents/{document_id}").status_code == 404


def test_http_bad_inputs(client):
    assert client.post("/api/documents", files={"file": ("bad.pdf", b"bad")}).status_code == 400
    for body in [
        {"question": " "},
        {"question": "x", "mode": "invalid"},
        {"question": "x", "document_id": "bad"},
    ]:
        assert client.post("/api/query", json=body).status_code == 422
    response = client.post("/api/query", json={"question": "x", "document_id": "a" * 64})
    assert response.status_code == 404
