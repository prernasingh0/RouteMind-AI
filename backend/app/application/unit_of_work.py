from sqlalchemy.ext.asyncio import AsyncSession
from app.domain import models
from app.domain.models import AuditLog, Organization, Permission, RefreshToken, Role, User
from app.infrastructure.repositories.generic import GenericRepository
from app.infrastructure.repositories.business import REPOSITORY_BY_MODEL

class UnitOfWork:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.organizations = GenericRepository(session, Organization)
        self.users = GenericRepository(session, User)
        self.roles = GenericRepository(session, Role)
        self.permissions = GenericRepository(session, Permission)
        self.refresh_tokens = GenericRepository(session, RefreshToken)
        self.audit_logs = GenericRepository(session, AuditLog)
        for model, repo_cls in REPOSITORY_BY_MODEL.items():
            setattr(self, model.__tablename__, repo_cls(session, model))
    async def commit(self) -> None: await self.session.commit()
    async def rollback(self) -> None: await self.session.rollback()
