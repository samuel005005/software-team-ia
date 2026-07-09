from dataclasses import dataclass
from uuid import UUID

from app.domain.enums import UserRole
from app.domain.auth.errors import ProfileNotFoundError


@dataclass(frozen=True)
class UserProfile:
    id: UUID
    email: str
    role: UserRole
    full_name: str
    phone: str | None = None
    bio: str | None = None
    photo_url: str | None = None


@dataclass(frozen=True)
class UpdateProfileCommand:
    full_name: str | None = None
    phone: str | None = None
    bio: str | None = None
    photo_url: str | None = None


def build_user_profile(user) -> UserProfile:
    if user.role == UserRole.CLIENT:
        if user.client_profile is None:
            raise ProfileNotFoundError()
        return UserProfile(
            id=user.id,
            email=user.email,
            role=user.role,
            full_name=user.client_profile.full_name,
            phone=user.client_profile.phone,
        )

    if user.role == UserRole.BARBER:
        if user.barber_profile is None:
            raise ProfileNotFoundError()
        return UserProfile(
            id=user.id,
            email=user.email,
            role=user.role,
            full_name=user.barber_profile.display_name,
            bio=user.barber_profile.bio,
            photo_url=user.barber_profile.photo_url,
        )

    return UserProfile(
        id=user.id,
        email=user.email,
        role=user.role,
        full_name=user.email,
    )
