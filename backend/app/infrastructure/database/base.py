from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4
from sqlalchemy import DateTime, MetaData, func
from app.infrastructure.database.types import GUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

convention = {"ix": "ix_%(column_0_label)s", "uq": "uq_%(table_name)s_%(column_0_name)s", "ck": "ck_%(table_name)s_%(constraint_name)s", "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s", "pk": "pk_%(table_name)s"}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=convention)

class UUIDPrimaryKeyMixin:
    id: Mapped[UUID] = mapped_column(GUID(), primary_key=True, default=uuid4)

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)

class BaseModel(Base, UUIDPrimaryKeyMixin, TimestampMixin, SoftDeleteMixin):
    __abstract__ = True
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return ''.join(['_' + c.lower() if c.isupper() else c for c in cls.__name__]).lstrip('_') + 's'
    def mark_deleted(self) -> None:
        self.deleted_at = datetime.now(timezone.utc)
