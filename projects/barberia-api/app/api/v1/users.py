from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.users.profile import UpdateProfileCommand, build_user_profile
from app.application.users.update_profile import (
    GetCurrentProfileQuery,
    GetCurrentProfileUseCase,
    UpdateMyProfileUseCase,
)
from app.core.dependencies.database import get_db
from app.core.dependencies.auth import get_current_user
from app.domain.auth.errors import (
    ProfileNotFoundError,
    ProfileUpdateForbiddenError,
)
from app.domain.enums import UserRole
from app.infrastructure.db.models.user import User
from app.schemas.users import UserProfileResponse, UserProfileUpdate

router = APIRouter()


def _to_response(profile) -> UserProfileResponse:
    return UserProfileResponse(
        id=profile.id,
        email=profile.email,
        role=profile.role,
        full_name=profile.full_name,
        phone=profile.phone,
        bio=profile.bio,
        photo_url=profile.photo_url,
    )


@router.get("/me", response_model=UserProfileResponse)
def get_me(current_user: User = Depends(get_current_user)) -> UserProfileResponse:
    try:
        profile = GetCurrentProfileUseCase().execute(GetCurrentProfileQuery(user=current_user))
    except ProfileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado",
        ) from exc

    return _to_response(profile)


@router.patch("/me", response_model=UserProfileResponse)
def update_me(
    body: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserProfileResponse:
    if current_user.role == UserRole.CLIENT:
        if body.full_name is None and body.phone is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe enviar al menos un campo para actualizar",
            )
    elif current_user.role == UserRole.BARBER:
        if body.full_name is None and body.bio is None and body.photo_url is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debe enviar al menos un campo para actualizar",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Perfil no editable para administradores en MVP",
        )

    use_case = UpdateMyProfileUseCase(db)
    try:
        profile = use_case.execute(
            current_user,
            UpdateProfileCommand(
                full_name=body.full_name,
                phone=body.phone,
                bio=body.bio,
                photo_url=body.photo_url,
            ),
        )
        db.commit()
    except ProfileNotFoundError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Perfil no encontrado",
        ) from exc
    except ProfileUpdateForbiddenError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No autorizado para editar perfil",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return _to_response(profile)
