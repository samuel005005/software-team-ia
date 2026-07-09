from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import EntitySchema


class BarberSummary(EntitySchema):
    user_id: UUID | str
    display_name: str
    bio: str | None = None
    photo_url: str | None = None
    is_bookable: bool = True


class BarberListResponse(BaseModel):
    items: list[BarberSummary]


class AdminBarberSummary(EntitySchema):
    user_id: UUID | str
    email: EmailStr
    display_name: str
    bio: str | None = None
    photo_url: str | None = None
    is_bookable: bool = True
    is_active: bool = True


class AdminBarberListResponse(BaseModel):
    items: list[AdminBarberSummary]


class BarberCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str = Field(min_length=2, max_length=255)
    bio: str | None = Field(default=None, max_length=2000)
    photo_url: str | None = Field(default=None, max_length=512)
    is_bookable: bool = True


class BarberUpdateRequest(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=255)
    bio: str | None = Field(default=None, max_length=2000)
    photo_url: str | None = Field(default=None, max_length=512)
    is_bookable: bool | None = None
    is_active: bool | None = None


class BarberServicesAssignmentRequest(BaseModel):
    service_ids: list[UUID | str] = Field(default_factory=list)
