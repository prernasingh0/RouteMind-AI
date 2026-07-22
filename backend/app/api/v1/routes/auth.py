from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.config.settings import get_settings
from app.infrastructure.database.session import get_session
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, TokenPair, UserMe
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenPair)
async def login(payload: LoginRequest, request: Request, session: AsyncSession = Depends(get_session)) -> TokenPair:
    access, refresh = await AuthService(session).login(payload.organization_slug, payload.email.lower(), payload.password, request.headers.get("user-agent"), request.client.host if request.client else None)
    return TokenPair(access_token=access, refresh_token=refresh, expires_in=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES * 60)

@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, session: AsyncSession = Depends(get_session)) -> TokenPair:
    access = await AuthService(session).refresh(payload.refresh_token)
    return TokenPair(access_token=access, refresh_token=payload.refresh_token, expires_in=get_settings().ACCESS_TOKEN_EXPIRE_MINUTES * 60)

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(payload: LogoutRequest, session: AsyncSession = Depends(get_session)) -> None:
    await AuthService(session).logout(payload.refresh_token)

@router.get("/me", response_model=UserMe)
async def me(user: UserMe = Depends(get_current_user)) -> UserMe:
    return user
