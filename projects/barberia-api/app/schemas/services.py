from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import EntitySchema


class ServiceSummary(EntitySchema):
    id: UUID | str
    name: str
    description: str | None = None
    duration_minutes: int
    price_dop: str
    is_active: bool = True


class ServiceListResponse(BaseModel):
    items: list[ServiceSummary]
