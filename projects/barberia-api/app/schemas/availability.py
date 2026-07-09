from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.schemas.barbers import BarberSummary


class AvailabilitySlot(BaseModel):
    start: datetime
    end: datetime
    barber_user_id: UUID | str


class AvailabilityResponse(BaseModel):
    service_id: UUID | str
    date: date
    barbers: list[BarberSummary]
    slots: list[AvailabilitySlot] = []
