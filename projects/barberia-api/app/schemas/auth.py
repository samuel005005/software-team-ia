from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import EntitySchema


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str = Field(min_length=2)
    phone: str = Field(min_length=7)


class RegisterResponse(EntitySchema):
    id: UUID
    email: EmailStr
    full_name: str
    message: str = "Registro exitoso"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str
