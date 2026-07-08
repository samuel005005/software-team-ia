from uuid import UUID

from pydantic import BaseModel

from app.schemas.common import EntitySchema


class BarberSummary(EntitySchema):
    user_id: UUID | str
    display_name: str
    bio: str | None = None
    photo_url: str | None = None
    is_bookable: bool = True


class BarberListResponse(BaseModel):
    items: list[BarberSummary]
