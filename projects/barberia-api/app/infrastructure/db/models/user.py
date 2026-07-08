import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import UserRole
from app.infrastructure.db.base import Base
from app.infrastructure.db.mixins import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.infrastructure.db.models.barber_profile import BarberProfile
    from app.infrastructure.db.models.client_profile import ClientProfile


def _enum_values(enum_cls: type) -> list[str]:
    return [item.value for item in enum_cls]


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", native_enum=True, values_callable=_enum_values),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    client_profile: Mapped["ClientProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    barber_profile: Mapped["BarberProfile | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
