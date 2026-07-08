import uuid

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base
from app.infrastructure.db.models.user import User


class BarberProfile(Base):
    __tablename__ = "barber_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_bookable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")

    user: Mapped[User] = relationship(back_populates="barber_profile")
