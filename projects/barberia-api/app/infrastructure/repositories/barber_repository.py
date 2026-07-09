from dataclasses import dataclass
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.domain.enums import UserRole
from app.infrastructure.db.models.barber_profile import BarberProfile
from app.infrastructure.db.models.barber_service import BarberService
from app.infrastructure.db.models.user import User


@dataclass(frozen=True)
class BarberPublicProfile:
    user_id: str
    display_name: str
    bio: str | None
    photo_url: str | None
    is_bookable: bool


@dataclass(frozen=True)
class BarberAdminRecord:
    user_id: str
    email: str
    display_name: str
    bio: str | None
    photo_url: str | None
    is_bookable: bool
    is_active: bool


class BarberRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_bookable(self, service_id: uuid.UUID | None = None) -> list[BarberPublicProfile]:
        stmt = (
            select(BarberProfile)
            .options(joinedload(BarberProfile.user))
            .where(BarberProfile.is_bookable.is_(True))
        )
        if service_id is not None:
            stmt = stmt.join(
                BarberService,
                BarberService.barber_user_id == BarberProfile.user_id,
            ).where(BarberService.service_id == service_id)

        rows = self._session.scalars(stmt.order_by(BarberProfile.display_name)).all()

        return [
            BarberPublicProfile(
                user_id=str(row.user_id),
                display_name=row.display_name,
                bio=row.bio,
                photo_url=row.photo_url,
                is_bookable=row.is_bookable,
            )
            for row in rows
            if row.user.is_active
        ]

    def list_all(self) -> list[BarberAdminRecord]:
        rows = self._session.scalars(
            select(User)
            .options(joinedload(User.barber_profile))
            .where(User.role == UserRole.BARBER)
            .order_by(User.email)
        ).all()

        records: list[BarberAdminRecord] = []
        for user in rows:
            if user.barber_profile is None:
                continue
            records.append(admin_record_from_user(user))
        records.sort(key=lambda item: item.display_name.lower())
        return records

    def get_barber_user(self, user_id: uuid.UUID) -> User | None:
        user = self._session.scalar(
            select(User)
            .options(joinedload(User.barber_profile))
            .where(User.id == user_id, User.role == UserRole.BARBER)
        )
        if user is None or user.barber_profile is None:
            return None
        return user


def admin_record_from_user(user: User) -> BarberAdminRecord:
    profile = user.barber_profile
    assert profile is not None
    return BarberAdminRecord(
        user_id=str(user.id),
        email=user.email,
        display_name=profile.display_name,
        bio=profile.bio,
        photo_url=profile.photo_url,
        is_bookable=profile.is_bookable,
        is_active=user.is_active,
    )
