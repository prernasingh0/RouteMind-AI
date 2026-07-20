import os
os.environ.setdefault("SECRET_KEY", "test-secret-key-change-me")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from app.infrastructure.database.base import Base
from app.infrastructure.database.session import get_session
from app.main import app
from app.domain.models import Organization, Permission, Role, User
from app.infrastructure.security.passwords import hash_password

@pytest_asyncio.fixture
async def session_factory():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        org = Organization(name="Acme Pharma", slug="acme", status="active", settings={})
        perm = Permission(code="users:read", description="Read users")
        role = Role(name="Representative", organization_id=None, permissions=[perm])
        user = User(organization=org, email="rep@acme.test", full_name="Rep User", hashed_password=hash_password("CorrectHorse1"), roles=[role])
        session.add(user); await session.commit()
    yield factory
    await engine.dispose()

@pytest_asyncio.fixture
async def client(session_factory):
    async def override_get_session():
        async with session_factory() as session:
            yield session
    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
