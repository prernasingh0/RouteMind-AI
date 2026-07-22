from uuid import UUID
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_session
from app.infrastructure.security.jwt import decode_token
from app.schemas.auth import UserMe

bearer = HTTPBearer(auto_error=False)

async def get_current_user(credentials: HTTPAuthorizationCredentials | None = Security(bearer), session: AsyncSession = Depends(get_session)) -> UserMe:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")
    payload = decode_token(credentials.credentials)
    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token type")
    return UserMe(id=UUID(payload["sub"]), organization_id=UUID(payload["org"]), email="user@example.com", full_name="Authenticated User", roles=payload.get("roles", []), permissions=payload.get("permissions", []))

def require_permissions(*required: str):
    async def checker(user: UserMe = Depends(get_current_user)) -> UserMe:
        if not set(required).issubset(set(user.permissions)):
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Insufficient permissions")
        return user
    return checker
