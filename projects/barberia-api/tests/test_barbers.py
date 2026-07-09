import uuid

from app.domain.enums import UserRole
from app.infrastructure.db.models.barber_profile import BarberProfile
from app.infrastructure.db.models.user import User
from app.infrastructure.security.password_hasher import hash_password
from tests.conftest import requires_db


def _create_barber(
    db_session,
    *,
    display_name: str,
    bio: str | None = None,
    photo_url: str | None = None,
    is_bookable: bool = True,
    is_active: bool = True,
) -> User:
    user = User(
        email=f"barber-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("password123"),
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
    return user


@requires_db
def test_list_barbers_returns_bookable_active_barbers(client, db_session) -> None:
    _create_barber(
        db_session,
        display_name="Ana Barber",
        bio="Cortes clásicos",
        photo_url="https://cdn.example.com/ana.jpg",
    )
    _create_barber(
        db_session,
        display_name="Carlos Oculto",
        is_bookable=False,
    )
    _create_barber(
        db_session,
        display_name="Inactivo",
        is_active=False,
    )

    response = client.get("/api/v1/barbers")

    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    barber = body["items"][0]
    assert barber["display_name"] == "Ana Barber"
    assert barber["bio"] == "Cortes clásicos"
    assert barber["photo_url"] == "https://cdn.example.com/ana.jpg"
    assert barber["is_bookable"] is True


@requires_db
def test_list_barbers_empty_when_none_bookable(client) -> None:
    response = client.get("/api/v1/barbers")

    assert response.status_code == 200
    assert response.json()["items"] == []
