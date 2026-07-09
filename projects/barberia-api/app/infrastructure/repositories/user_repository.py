import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.domain.enums import UserRole
from app.infrastructure.db.models.barber_profile import BarberProfile
from app.infrastructure.db.models.client_profile import ClientProfile
from app.infrastructure.db.models.user import User


@dataclass(frozen=True)
class CreateClientData:
    email: str
    password_hash: str
    full_name: str
    phone: str


@dataclass(frozen=True)
class CreateBarberData:
    email: str
    password_hash: str
    display_name: str
    bio: str | None = None
    photo_url: str | None = None
    is_bookable: bool = True


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_email(self, email: str) -> User | None:
        normalized = email.strip().lower()
        return self._session.scalar(select(User).where(User.email == normalized))

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self._session.get(User, user_id)

    def get_by_id_with_profiles(self, user_id: uuid.UUID) -> User | None:
        return self._session.scalar(
            select(User)
            .options(
                joinedload(User.client_profile),
                joinedload(User.barber_profile),
            )
            .where(User.id == user_id)
        )

    def create_client(self, data: CreateClientData) -> User:
        user = User(
            email=data.email.strip().lower(),
            password_hash=data.password_hash,
            role=UserRole.CLIENT,
            is_active=True,
        )
        user.client_profile = ClientProfile(
            full_name=data.full_name.strip(),
            phone=data.phone.strip(),
        )
        self._session.add(user)
        self._session.flush()
        return user

    def update_client_profile(
        self,
        user: User,
        *,
        full_name: str | None = None,
        phone: str | None = None,
    ) -> User:
        if user.client_profile is None:
            raise ValueError("Client profile missing")

        if full_name is not None:
            user.client_profile.full_name = full_name.strip()
        if phone is not None:
            user.client_profile.phone = phone.strip()
        self._session.flush()
        return user

    def update_client_admin(
        self,
        user: User,
        *,
        is_active: bool | None = None,
    ) -> User:
        if user.client_profile is None:
            raise ValueError("Client profile missing")

        if is_active is not None:
            user.is_active = is_active
        self._session.flush()
        return user

    def create_barber(self, data: CreateBarberData) -> User:
        user = User(
            email=data.email.strip().lower(),
            password_hash=data.password_hash,
            role=UserRole.BARBER,
            is_active=True,
        )
        user.barber_profile = BarberProfile(
            display_name=data.display_name.strip(),
            bio=data.bio.strip() if data.bio else None,
            photo_url=data.photo_url.strip() if data.photo_url else None,
            is_bookable=data.is_bookable,
        )
        self._session.add(user)
        self._session.flush()
        return user

    def update_barber_admin(
        self,
        user: User,
        *,
        display_name: str | None = None,
        bio: str | None = None,
        photo_url: str | None = None,
        is_bookable: bool | None = None,
        is_active: bool | None = None,
    ) -> User:
        if user.barber_profile is None:
            raise ValueError("Barber profile missing")

        if display_name is not None:
            user.barber_profile.display_name = display_name.strip()
        if bio is not None:
            user.barber_profile.bio = bio.strip() or None
        if photo_url is not None:
            user.barber_profile.photo_url = photo_url.strip() or None
        if is_bookable is not None:
            user.barber_profile.is_bookable = is_bookable
        if is_active is not None:
            user.is_active = is_active
        self._session.flush()
        return user

    def update_barber_profile(
        self,
        user: User,
        *,
        display_name: str | None = None,
        bio: str | None = None,
        photo_url: str | None = None,
    ) -> User:
        if user.barber_profile is None:
            raise ValueError("Barber profile missing")

        if display_name is not None:
            user.barber_profile.display_name = display_name.strip()
        if bio is not None:
            user.barber_profile.bio = bio.strip() or None
        if photo_url is not None:
            user.barber_profile.photo_url = photo_url.strip() or None
        self._session.flush()
        return user
