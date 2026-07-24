from uuid import UUID
from fastapi import Depends, HTTPException, Security, status
from jose import JWTError
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.infrastructure.database.session import get_session
from app.infrastructure.security.jwt import decode_token
from app.domain.models import Role, User
from app.schemas.auth import UserMe

bearer = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Security(bearer), session: AsyncSession = Depends(get_session)) -> UserMe:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")
    try:
        payload = decode_token(credentials.credentials)
    except (JWTError, ValueError, KeyError) as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token") from exc
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")
    try:
        user_id = UUID(payload["sub"])
        organization_id = UUID(payload["org"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token claims") from exc
    user = await session.get(
        User,
        user_id,
        options=[selectinload(User.roles).selectinload(Role.permissions)],
    )
    if (
        user is None
        or user.deleted_at is not None
        or not user.is_active
        or user.organization_id != organization_id
    ):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User is no longer active")
    roles = [role.name for role in user.roles if role.deleted_at is None]
    permissions = sorted(
        {
            permission.code
            for role in user.roles
            if role.deleted_at is None
            for permission in role.permissions
            if permission.deleted_at is None
        }
    )
    return UserMe(
        id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        full_name=user.full_name,
        roles=roles,
        permissions=permissions,
    )

def require_permissions(*required: str):
    async def checker(user: UserMe = Depends(get_current_user)) -> UserMe:
        if not set(required).issubset(set(user.permissions)):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return checker
