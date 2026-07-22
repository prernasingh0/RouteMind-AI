from sqlalchemy import CHAR, JSON, String, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from uuid import UUID

class GUID(TypeDecorator):
    impl = CHAR
    cache_ok = True
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql": return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))
    def process_bind_param(self, value, dialect):
        if value is None: return None
        if dialect.name == "postgresql": return value
        return str(value)
    def process_result_value(self, value, dialect):
        if value is None: return None
        if isinstance(value, UUID): return value
        return UUID(value)

class JSONDict(TypeDecorator):
    impl = JSON
    cache_ok = True

class IPAddress(TypeDecorator):
    impl = String(45)
    cache_ok = True
