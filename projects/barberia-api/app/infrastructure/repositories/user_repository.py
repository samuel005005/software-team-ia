import uuid
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.enums import UserRole
from app.infrastructure.db.models.client_profile import ClientProfile
from app.infrastructure.db.models.user import User


@dataclass(frozen=True)
class CreateClientData:
    email: str
    password_hash: str
    full_name: str
    phone: str


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_email(self, email: str) -> User | None:
        normalized = email.strip().lower()
        return self._session.scalar(select(User).where(User.email == normalized))

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

    def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return self._session.get(User, user_id)
