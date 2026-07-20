from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config.settings import get_settings

settings = get_settings()
engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True, future=True)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session
