import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import Settings, get_settings
from app.domain.enums import UserRole


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def generate_refresh_token() -> tuple[str, str]:
    plain = secrets.token_urlsafe(32)
    return plain, hash_token(plain)


class JwtService:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    def create_access_token(self, user_id: uuid.UUID, email: str, role: UserRole) -> str:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=self._settings.access_token_expire_minutes
        )
        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role.value,
            "type": "access",
            "exp": expire,
        }
        return jwt.encode(payload, self._settings.secret_key, algorithm="HS256")

    def decode_access_token(self, token: str) -> dict:
        payload = jwt.decode(token, self._settings.secret_key, algorithms=["HS256"])
        if payload.get("type") != "access":
            raise JWTError("Invalid token type")
        return payload

    def refresh_token_expires_at(self) -> datetime:
        return datetime.now(timezone.utc) + timedelta(days=self._settings.refresh_token_expire_days)
