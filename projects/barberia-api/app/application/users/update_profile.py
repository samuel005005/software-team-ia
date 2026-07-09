from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.application.users.profile import UpdateProfileCommand, UserProfile, build_user_profile
from app.domain.auth.errors import ProfileNotFoundError, ProfileUpdateForbiddenError
from app.domain.enums import UserRole
from app.infrastructure.db.models.user import User
from app.infrastructure.repositories.user_repository import UserRepository


@dataclass(frozen=True)
class GetCurrentProfileQuery:
    user: User


class GetCurrentProfileUseCase:
    def execute(self, query: GetCurrentProfileQuery) -> UserProfile:
        return build_user_profile(query.user)


class UpdateMyProfileUseCase:
    def __init__(self, session: Session) -> None:
        self._users = UserRepository(session)

    def execute(self, user: User, command: UpdateProfileCommand) -> UserProfile:
        if user.role == UserRole.CLIENT:
            return self._update_client(user, command)
        if user.role == UserRole.BARBER:
            return self._update_barber(user, command)
        raise ProfileUpdateForbiddenError()

    def _update_client(self, user: User, command: UpdateProfileCommand) -> UserProfile:
        if user.client_profile is None:
            raise ProfileNotFoundError()
        if command.full_name is None and command.phone is None:
            return build_user_profile(user)
        updated = self._users.update_client_profile(
            user,
            full_name=command.full_name,
            phone=command.phone,
        )
        return build_user_profile(updated)

    def _update_barber(self, user: User, command: UpdateProfileCommand) -> UserProfile:
        if user.barber_profile is None:
            raise ProfileNotFoundError()
        if (
            command.full_name is None
            and command.bio is None
            and command.photo_url is None
        ):
            return build_user_profile(user)
        updated = self._users.update_barber_profile(
            user,
            display_name=command.full_name,
            bio=command.bio,
            photo_url=command.photo_url,
        )
        return build_user_profile(updated)
