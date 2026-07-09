from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.domain.enums import UserRole
from app.schemas.common import EntitySchema


class UserProfileResponse(EntitySchema):
    id: UUID | str
    email: EmailStr
    role: UserRole
    full_name: str
    phone: str | None = None
    bio: str | None = None
    photo_url: str | None = None


class UserProfileUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2)
    phone: str | None = Field(default=None, min_length=7)
    bio: str | None = Field(default=None, max_length=2000)
    photo_url: str | None = Field(default=None, max_length=512)
