from datetime import datetime, timedelta, timezone
from hashlib import sha256
from secrets import token_urlsafe
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.config.settings import get_settings
from app.domain.models import Organization, RefreshToken, Role, User
from app.infrastructure.security.jwt import create_access_token
from app.infrastructure.security.passwords import verify_password

settings = get_settings()

def _hash_refresh(token: str) -> str: return sha256(token.encode()).hexdigest()

def _roles_permissions(user: User) -> tuple[list[str], list[str]]:
    roles = [r.name for r in user.roles if r.deleted_at is None]
    perms = sorted({p.code for r in user.roles for p in r.permissions if p.deleted_at is None})
    return roles, perms

class AuthService:
    def __init__(self, session: AsyncSession) -> None: self.session = session
    async def login(self, organization_slug: str, email: str, password: str, user_agent: str | None, ip: str | None):
        stmt = select(User).options(selectinload(User.roles).selectinload(Role.permissions)).join(Organization).where(Organization.slug == organization_slug, User.email == email.lower(), User.deleted_at.is_(None), Organization.deleted_at.is_(None))
        user = await self.session.scalar(stmt)
        if not user or not user.is_active or not verify_password(password, user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
        roles, perms = _roles_permissions(user)
        raw_refresh = token_urlsafe(48)
        refresh = RefreshToken(user_id=user.id, token_hash=_hash_refresh(raw_refresh), expires_at=datetime.now(timezone.utc)+timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), user_agent=user_agent, ip_address=ip)
        user.last_login_at = datetime.now(timezone.utc)
        self.session.add_all([refresh, user]); await self.session.commit(); await self.session.refresh(user)
        return create_access_token(user_id=user.id, organization_id=user.organization_id, roles=roles, permissions=perms), raw_refresh
    async def refresh(self, raw_refresh: str):
        token = await self.session.scalar(select(RefreshToken).where(RefreshToken.token_hash == _hash_refresh(raw_refresh), RefreshToken.revoked_at.is_(None), RefreshToken.deleted_at.is_(None)))
        if not token or token.expires_at.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid refresh token")
        user = await self.session.get(User, token.user_id, options=[selectinload(User.roles).selectinload(Role.permissions)])
        if not user or not user.is_active:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Inactive user")
        roles, perms = _roles_permissions(user)
        return create_access_token(user_id=user.id, organization_id=user.organization_id, roles=roles, permissions=perms)
    async def logout(self, raw_refresh: str) -> None:
        token = await self.session.scalar(select(RefreshToken).where(RefreshToken.token_hash == _hash_refresh(raw_refresh)))
        if token and token.revoked_at is None:
            token.revoked_at = datetime.now(timezone.utc); self.session.add(token); await self.session.commit()
