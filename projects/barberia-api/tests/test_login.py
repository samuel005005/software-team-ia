import uuid

import pytest
from jose import jwt

from app.core.config import get_settings
from app.domain.enums import UserRole
from app.infrastructure.db.models.user import User
from tests.conftest import requires_db


def _register(client, email: str | None = None, password: str = "password123") -> dict:
    addr = email or f"auth-{uuid.uuid4().hex[:8]}@test.com"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": addr,
            "password": password,
            "full_name": "Auth Test",
            "phone": "8095554321",
        },
    )
    assert response.status_code == 201
    return {"email": addr, "password": password}


@requires_db
def test_login_success_returns_tokens(client) -> None:
    creds = _register(client)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": creds["email"], "password": creds["password"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]

    settings = get_settings()
    payload = jwt.decode(body["access_token"], settings.secret_key, algorithms=["HS256"])
    assert payload["type"] == "access"
    assert payload["role"] == UserRole.CLIENT.value
    assert payload["email"] == creds["email"]


@requires_db
def test_login_invalid_credentials_returns_401(client) -> None:
    creds = _register(client)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": creds["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales incorrectas"


@requires_db
def test_login_unknown_email_returns_401(client) -> None:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "unknown@test.com", "password": "password123"},
    )
    assert response.status_code == 401


@requires_db
def test_login_inactive_user_returns_403(client, db_session) -> None:
    creds = _register(client)
    user = db_session.query(User).filter_by(email=creds["email"]).one()
    user.is_active = False
    db_session.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={"email": creds["email"], "password": creds["password"]},
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Cuenta desactivada"


@requires_db
def test_refresh_returns_new_tokens(client) -> None:
    creds = _register(client)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": creds["email"], "password": creds["password"]},
    )
    refresh_token = login.json()["refresh_token"]

    response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    body = response.json()
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["refresh_token"] != refresh_token


@requires_db
def test_refresh_rotates_token_old_becomes_invalid(client) -> None:
    creds = _register(client)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": creds["email"], "password": creds["password"]},
    )
    old_refresh = login.json()["refresh_token"]

    refresh = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert refresh.status_code == 200

    reuse = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert reuse.status_code == 401


@requires_db
def test_refresh_invalid_token_returns_401(client) -> None:
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "not-a-valid-token"},
    )
    assert response.status_code == 401


@requires_db
def test_register_then_login_flow(client) -> None:
    creds = _register(client)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": creds["email"], "password": creds["password"]},
    )
    assert login.status_code == 200
