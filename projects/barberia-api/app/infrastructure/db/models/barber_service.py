import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base


class BarberService(Base):
    __tablename__ = "barber_services"
    __table_args__ = (
        UniqueConstraint("barber_user_id", "service_id", name="uq_barber_services_barber_service"),
    )

    barber_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("barber_profiles.user_id", ondelete="CASCADE"),
        primary_key=True,
    )
    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("services.id", ondelete="CASCADE"),
        primary_key=True,
    )
