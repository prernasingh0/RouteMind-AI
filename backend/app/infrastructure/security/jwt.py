from datetime import datetime, timedelta, timezone
from uuid import UUID
from jose import JWTError, jwt
from app.config.settings import get_settings

settings = get_settings()

def create_access_token(*, user_id: UUID, organization_id: UUID, roles: list[str], permissions: list[str]) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": str(user_id), "org": str(organization_id), "roles": roles, "permissions": permissions, "type": "access", "iat": now, "exp": now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
