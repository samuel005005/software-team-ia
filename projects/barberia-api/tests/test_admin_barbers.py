import uuid

from app.domain.enums import UserRole
from app.infrastructure.db.models.barber_profile import BarberProfile
from app.infrastructure.db.models.user import User
from app.infrastructure.security.password_hasher import hash_password
from tests.conftest import requires_db
from tests.test_role_guards import _auth, _create_user_and_login, _register_client


def _create_barber(
    db_session,
    *,
    email: str | None = None,
    display_name: str = "Barbero Test",
    is_bookable: bool = True,
    is_active: bool = True,
) -> User:
    user = User(
        email=email or f"barber-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("password123"),
        role=UserRole.BARBER,
        is_active=is_active,
    )
    user.barber_profile = BarberProfile(
        display_name=display_name,
        is_bookable=is_bookable,
    )
    db_session.add(user)
    db_session.commit()
    return user


@requires_db
def test_admin_list_barbers_includes_inactive(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    _create_barber(db_session, display_name="Activo")
    _create_barber(db_session, display_name="Inactivo", is_active=False)

    response = client.get("/api/v1/admin/barbers", headers=_auth(admin_token))

    assert response.status_code == 200
    names = [item["display_name"] for item in response.json()["items"]]
    assert names == ["Activo", "Inactivo"]


@requires_db
def test_admin_create_barber(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)

    response = client.post(
        "/api/v1/admin/barbers",
        headers=_auth(admin_token),
        json={
            "email": "nuevo.barbero@test.com",
            "password": "password123",
            "display_name": "Nuevo Barbero",
            "bio": "Especialista",
            "is_bookable": True,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "nuevo.barbero@test.com"
    assert body["display_name"] == "Nuevo Barbero"
    assert body["is_active"] is True

    public = client.get("/api/v1/barbers")
    assert len(public.json()["items"]) == 1


@requires_db
def test_admin_update_barber_deactivates(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    barber = _create_barber(db_session, display_name="Temporal")

    response = client.patch(
        f"/api/v1/admin/barbers/{barber.id}",
        headers=_auth(admin_token),
        json={"is_active": False, "is_bookable": False},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["is_active"] is False
    assert body["is_bookable"] is False

    public = client.get("/api/v1/barbers")
    assert public.json()["items"] == []


@requires_db
def test_admin_barbers_reject_client(client) -> None:
    token, _ = _register_client(client)
    response = client.get("/api/v1/admin/barbers", headers=_auth(token))
    assert response.status_code == 403


@requires_db
def test_admin_create_barber_duplicate_email(client, db_session) -> None:
    admin_token, _ = _create_user_and_login(client, db_session, role=UserRole.ADMIN)
    _create_barber(db_session, email="duplicado@test.com")

    response = client.post(
        "/api/v1/admin/barbers",
        headers=_auth(admin_token),
        json={
            "email": "duplicado@test.com",
            "password": "password123",
            "display_name": "Otro",
        },
    )

    assert response.status_code == 409
