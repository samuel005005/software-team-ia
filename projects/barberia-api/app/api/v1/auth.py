from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.application.auth.login import LoginCommand, LoginUseCase, RefreshSessionCommand, RefreshSessionUseCase
from app.application.auth.register_client import RegisterClientCommand, RegisterClientUseCase
from app.core.dependencies import get_db
from app.domain.auth.errors import (
    EmailAlreadyExistsError,
    InactiveUserError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    TokenResponse,
)

router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    use_case = RegisterClientUseCase(db)
    try:
        result = use_case.execute(
            RegisterClientCommand(
                email=body.email,
                password=body.password,
                full_name=body.full_name,
                phone=body.phone,
            )
        )
        db.commit()
    except EmailAlreadyExistsError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El email ya está registrado",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return RegisterResponse(
        id=result.user_id,
        email=result.email,
        full_name=result.full_name,
    )


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    use_case = LoginUseCase(db)
    try:
        result = use_case.execute(LoginCommand(email=body.email, password=body.password))
        db.commit()
    except InvalidCredentialsError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        ) from exc
    except InactiveUserError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta desactivada",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return TokenResponse(access_token=result.access_token, refresh_token=result.refresh_token)


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    use_case = RefreshSessionUseCase(db)
    try:
        result = use_case.execute(RefreshSessionCommand(refresh_token=body.refresh_token))
        db.commit()
    except InvalidRefreshTokenError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
        ) from exc
    except Exception:
        db.rollback()
        raise

    return TokenResponse(access_token=result.access_token, refresh_token=result.refresh_token)
