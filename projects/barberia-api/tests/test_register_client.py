import uuid

import pytest
from sqlalchemy import select

from app.application.auth.register_client import RegisterClientCommand, RegisterClientUseCase
from app.domain.auth.errors import EmailAlreadyExistsError
from app.domain.enums import UserRole
from app.infrastructure.db.models.client_profile import ClientProfile
from app.infrastructure.db.models.user import User
from app.infrastructure.security.password_hasher import verify_password
from tests.conftest import requires_db


@requires_db
def test_register_client_success(client) -> None:
    email = f"client-{uuid.uuid4().hex[:8]}@test.com"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": "Juan Pérez",
            "phone": "8095551234",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == email
    assert body["full_name"] == "Juan Pérez"
    assert body["message"] == "Registro exitoso"
    assert body["id"]


@requires_db
def test_register_duplicate_email_returns_409(client) -> None:
    email = f"dup-{uuid.uuid4().hex[:8]}@test.com"
    payload = {
        "email": email,
        "password": "password123",
        "full_name": "Cliente Uno",
        "phone": "8095550001",
    }
    first = client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409
    assert second.json()["detail"] == "El email ya está registrado"


@requires_db
def test_register_normalizes_email(client, db_session) -> None:
    local = uuid.uuid4().hex[:8]
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"  MixedCase-{local}@Test.COM  ",
            "password": "password123",
            "full_name": "Cliente",
            "phone": "8095559999",
        },
    )
    assert response.status_code == 201

    stored = db_session.scalar(
        select(User).where(User.email == f"mixedcase-{local}@test.com")
    )
    assert stored is not None
    assert stored.role == UserRole.CLIENT


@requires_db
def test_register_stores_hashed_password(client, db_session) -> None:
    email = f"hash-{uuid.uuid4().hex[:8]}@test.com"
    password = "password123"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Cliente",
            "phone": "8095558888",
        },
    )
    assert response.status_code == 201

    user = db_session.scalar(select(User).where(User.email == email))
    assert user is not None
    assert user.password_hash != password
    assert verify_password(password, user.password_hash)


@requires_db
def test_register_creates_client_profile(client, db_session) -> None:
    email = f"profile-{uuid.uuid4().hex[:8]}@test.com"
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "password123",
            "full_name": "María López",
            "phone": "8095557777",
        },
    )
    assert response.status_code == 201

    user = db_session.scalar(select(User).where(User.email == email))
    profile = db_session.get(ClientProfile, user.id)
    assert profile is not None
    assert profile.full_name == "María López"
    assert profile.phone == "8095557777"


@requires_db
def test_register_validates_password_length(client) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"short-{uuid.uuid4().hex[:8]}@test.com",
            "password": "short",
            "full_name": "Cliente",
            "phone": "8095556666",
        },
    )
    assert response.status_code == 422


@requires_db
def test_register_client_use_case_duplicate_raises(db_session) -> None:
    email = f"usecase-{uuid.uuid4().hex[:8]}@test.com"
    use_case = RegisterClientUseCase(db_session)
    command = RegisterClientCommand(
        email=email,
        password="password123",
        full_name="Test",
        phone="8095551111",
    )
    use_case.execute(command)
    db_session.commit()

    with pytest.raises(EmailAlreadyExistsError):
        use_case.execute(command)
