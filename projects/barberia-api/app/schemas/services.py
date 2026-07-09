from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

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


class ServiceCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    duration_minutes: int = Field(gt=0, le=480)
    price_dop: Decimal = Field(gt=0)
    is_active: bool = True


class ServiceUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    duration_minutes: int | None = Field(default=None, gt=0, le=480)
    price_dop: Decimal | None = Field(default=None, gt=0)
    is_active: bool | None = None
