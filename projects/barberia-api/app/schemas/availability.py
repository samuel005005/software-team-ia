from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AvailabilitySlot(BaseModel):
    start: datetime
    end: datetime
    barber_user_id: UUID | str


class AvailabilityResponse(BaseModel):
    service_id: UUID | str
    date: str
    slots: list[AvailabilitySlot]
