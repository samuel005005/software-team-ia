from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

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


class BarberScheduleAppointmentResponse(EntitySchema):
    id: UUID | str
    status: AppointmentStatus
    scheduled_start: datetime
    scheduled_end: datetime
    service_id: UUID | str
    service_name: str
    client_user_id: UUID | str
    client_display_name: str


class BarberScheduleResponse(BaseModel):
    from_date: date
    to_date: date
    items: list[BarberScheduleAppointmentResponse]


class UpdateAppointmentStatusRequest(BaseModel):
    status: AppointmentStatus


class VoidAppointmentRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=500)
