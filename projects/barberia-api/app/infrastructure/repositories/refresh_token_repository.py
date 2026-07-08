from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.infrastructure.db.models.refresh_token import RefreshToken
from app.infrastructure.security.jwt_service import hash_token


class RefreshTokenRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, user_id, token_hash: str, expires_at: datetime) -> RefreshToken:
        record = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self._session.add(record)
        self._session.flush()
        return record

    def get_valid_by_plain_token(self, plain_token: str) -> RefreshToken | None:
        token_hash = hash_token(plain_token)
        now = datetime.now(timezone.utc)
        return self._session.scalar(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now,
            )
        )

    def revoke(self, record: RefreshToken) -> None:
        record.revoked_at = datetime.now(timezone.utc)
        self._session.flush()
