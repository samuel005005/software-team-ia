from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.domain.enums import AppointmentStatus
from app.schemas.common import EntitySchema


class AdminClientSummary(EntitySchema):
    user_id: UUID | str
    email: EmailStr
    full_name: str
    phone: str
    is_active: bool = True


class AdminClientListResponse(BaseModel):
    items: list[AdminClientSummary]


class ClientUpdateRequest(BaseModel):
    is_active: bool | None = None


class AdminClientAppointmentSummary(EntitySchema):
    id: UUID | str
    status: AppointmentStatus
    scheduled_start: datetime
    scheduled_end: datetime
    service_name: str = Field(min_length=1)
    barber_display_name: str = Field(min_length=1)


class AdminClientAppointmentListResponse(BaseModel):
    items: list[AdminClientAppointmentSummary]
