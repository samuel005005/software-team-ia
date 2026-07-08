from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.domain.enums import UserRole
from app.schemas.common import EntitySchema


class UserProfileResponse(EntitySchema):
    id: UUID | str
    email: EmailStr
    role: UserRole
    full_name: str
    phone: str | None = None


class UserProfileUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
