from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class LoginRequest(BaseModel):
    organization_slug: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8)

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=32)

class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=32)

class UserMe(BaseModel):
    id: UUID
    organization_id: UUID
    email: EmailStr
    full_name: str
    roles: list[str]
    permissions: list[str]
