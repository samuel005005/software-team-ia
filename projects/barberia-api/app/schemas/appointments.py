from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums import AppointmentStatus
from app.schemas.common import EntitySchema


class AppointmentCreateRequest(BaseModel):
    barber_user_id: UUID | str
    service_id: UUID | str
    scheduled_start: datetime


class AppointmentResponse(EntitySchema):
    id: UUID | str
    status: AppointmentStatus
    scheduled_start: datetime
    scheduled_end: datetime
    service_id: UUID | str
    service_name: str
    barber_user_id: UUID | str
    barber_display_name: str


class AppointmentListResponse(BaseModel):
    items: list[AppointmentResponse]
