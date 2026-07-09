import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_root_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_v1_health(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "barberia-api"


def test_auth_login_stub_returns_501(client: TestClient) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "unknown@test.com", "password": "password123"},
    )
    assert response.status_code == 401


def test_me_endpoint_requires_auth(client: TestClient) -> None:
    response = client.get("/api/v1/me")
    assert response.status_code == 401


def test_openapi_docs_available(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Barberia API"
