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


class AppointmentListResponse(BaseModel):
    items: list[AppointmentResponse]
