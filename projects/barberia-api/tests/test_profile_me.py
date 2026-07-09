import uuid

from app.domain.enums import UserRole
from app.infrastructure.db.models.barber_profile import BarberProfile
from app.infrastructure.db.models.user import User
from app.infrastructure.security.password_hasher import hash_password
from tests.conftest import requires_db


def _register_and_login(client, email: str | None = None) -> tuple[str, str]:
    addr = email or f"profile-{uuid.uuid4().hex[:8]}@test.com"
    password = "password123"
    client.post(
        "/api/v1/auth/register",
        json={
            "email": addr,
            "password": password,
            "full_name": "Cliente Original",
            "phone": "8095551111",
        },
    )
    login = client.post(
        "/api/v1/auth/login",
        json={"email": addr, "password": password},
    )
    body = login.json()
    return body["access_token"], addr


def _create_barber_and_login(
    client,
    db_session,
    *,
    email: str | None = None,
    display_name: str = "Barbero Original",
    bio: str | None = "Bio original",
    photo_url: str | None = None,
    is_bookable: bool = True,
    is_active: bool = True,
) -> tuple[str, str]:
    addr = email or f"barber-{uuid.uuid4().hex[:8]}@test.com"
    password = "password123"
    user = User(
        email=addr,
        password_hash=hash_password(password),
        role=UserRole.BARBER,
        is_active=is_active,
    )
    user.barber_profile = BarberProfile(
        display_name=display_name,
        bio=bio,
        photo_url=photo_url,
        is_bookable=is_bookable,
    )
    db_session.add(user)
    db_session.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={"email": addr, "password": password},
    )
    body = login.json()
    return body["access_token"], addr


@requires_db
def test_get_me_returns_client_profile(client) -> None:
    token, email = _register_and_login(client)
    response = client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == email
    assert body["role"] == "client"
    assert body["full_name"] == "Cliente Original"
    assert body["phone"] == "8095551111"


@requires_db
def test_get_me_returns_barber_profile(client, db_session) -> None:
    token, email = _create_barber_and_login(client, db_session)
    response = client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == email
    assert body["role"] == "barber"
    assert body["full_name"] == "Barbero Original"
    assert body["bio"] == "Bio original"
    assert body.get("phone") is None


@requires_db
def test_get_me_requires_auth(client) -> None:
    response = client.get("/api/v1/me")
    assert response.status_code == 401


@requires_db
def test_patch_me_updates_client_profile(client) -> None:
    token, _ = _register_and_login(client)
    response = client.patch(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Nombre Actualizado", "phone": "8095559999"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "Nombre Actualizado"
    assert body["phone"] == "8095559999"

    get_response = client.get(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.json()["full_name"] == "Nombre Actualizado"


@requires_db
def test_patch_me_updates_barber_profile(client, db_session) -> None:
    token, _ = _create_barber_and_login(client, db_session)
    response = client.patch(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Barbero Pro",
            "bio": "Especialista en fades",
            "photo_url": "https://cdn.example.com/barber.jpg",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["full_name"] == "Barbero Pro"
    assert body["bio"] == "Especialista en fades"
    assert body["photo_url"] == "https://cdn.example.com/barber.jpg"


@requires_db
def test_patch_me_requires_at_least_one_field(client) -> None:
    token, _ = _register_and_login(client)
    response = client.patch(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert response.status_code == 400


@requires_db
def test_patch_me_barber_requires_at_least_one_field(client, db_session) -> None:
    token, _ = _create_barber_and_login(client, db_session)
    response = client.patch(
        "/api/v1/me",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert response.status_code == 400
