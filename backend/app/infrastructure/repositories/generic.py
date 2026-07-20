from typing import Generic, TypeVar
from uuid import UUID
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.base import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)

class GenericRepository(Generic[ModelT]):
    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self.session = session
        self.model = model
    def query(self) -> Select[tuple[ModelT]]:
        return select(self.model).where(self.model.deleted_at.is_(None))
    async def get(self, entity_id: UUID) -> ModelT | None:
        return await self.session.scalar(self.query().where(self.model.id == entity_id))
    async def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        return entity
    async def list(self, *, limit: int = 100, offset: int = 0) -> list[ModelT]:
        return list((await self.session.scalars(self.query().limit(limit).offset(offset))).all())
    async def delete(self, entity: ModelT) -> None:
        entity.mark_deleted(); self.session.add(entity)
