from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.repositories.business import REPOSITORY_BY_MODEL

class TenantCrudService:
    def __init__(self, session: AsyncSession, model) -> None:
        self.session = session; self.model = model; self.repo = REPOSITORY_BY_MODEL[model](session, model)
    async def create(self, organization_id: UUID, payload):
        entity = self.model(organization_id=organization_id, **payload.model_dump(exclude_unset=True))
        self.session.add(entity); await self.session.commit(); await self.session.refresh(entity); return entity
    async def get(self, organization_id: UUID, entity_id: UUID):
        entity = await self.repo.get_for_tenant(organization_id, entity_id)
        if not entity: raise HTTPException(status.HTTP_404_NOT_FOUND, f"{self.model.__name__} not found")
        return entity
    async def list(self, organization_id: UUID, *, limit: int, offset: int, sort: str, search: str | None):
        return await self.repo.list_for_tenant(organization_id, limit=limit, offset=offset, sort=sort, search=search)
    async def update(self, organization_id: UUID, entity_id: UUID, payload):
        entity = await self.get(organization_id, entity_id)
        for key, value in payload.model_dump(exclude_unset=True).items(): setattr(entity, key, value)
        self.session.add(entity); await self.session.commit(); await self.session.refresh(entity); return entity
    async def delete(self, organization_id: UUID, entity_id: UUID):
        entity = await self.get(organization_id, entity_id)
        entity.mark_deleted(); self.session.add(entity); await self.session.commit()
