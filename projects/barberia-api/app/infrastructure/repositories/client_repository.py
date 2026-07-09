from dataclasses import dataclass
import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.domain.enums import UserRole
from app.infrastructure.db.models.client_profile import ClientProfile
from app.infrastructure.db.models.user import User


@dataclass(frozen=True)
class ClientAdminRecord:
    user_id: str
    email: str
    full_name: str
    phone: str
    is_active: bool


def admin_record_from_user(user: User) -> ClientAdminRecord:
    profile = user.client_profile
    if profile is None:
        raise ValueError("Client profile missing")

    return ClientAdminRecord(
        user_id=str(user.id),
        email=user.email,
        full_name=profile.full_name,
        phone=profile.phone,
        is_active=user.is_active,
    )


class ClientRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_all(self) -> list[ClientAdminRecord]:
        rows = self._session.scalars(
            select(User)
            .options(joinedload(User.client_profile))
            .where(User.role == UserRole.CLIENT)
            .order_by(User.email)
        ).all()

        return [admin_record_from_user(row) for row in rows if row.client_profile is not None]

    def get_client_user(self, user_id: uuid.UUID) -> User | None:
        return self._session.scalar(
            select(User)
            .options(joinedload(User.client_profile))
            .where(User.id == user_id, User.role == UserRole.CLIENT)
        )
