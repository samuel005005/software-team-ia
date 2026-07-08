from datetime import time
import uuid

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base
from app.infrastructure.db.mixins import UUIDPrimaryKeyMixin


class BusinessHours(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "business_hours"
    __table_args__ = (
        CheckConstraint("weekday >= 1 AND weekday <= 7", name="ck_business_hours_weekday"),
    )

    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    open_time: Mapped[time] = mapped_column(Time, nullable=False)
    close_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")


class BarberAvailability(Base, UUIDPrimaryKeyMixin):
    __tablename__ = "barber_availability"
    __table_args__ = (
        CheckConstraint("weekday >= 1 AND weekday <= 7", name="ck_barber_availability_weekday"),
    )

    barber_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("barber_profiles.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    weekday: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
