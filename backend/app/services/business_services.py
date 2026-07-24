from sqlalchemy.ext.asyncio import AsyncSession
from app.domain import models
from app.services.crud import TenantCrudService

class DoctorService(TenantCrudService):
    def __init__(self, session: AsyncSession): super().__init__(session, models.HCP)
class VisitService(TenantCrudService):
    def __init__(self, session: AsyncSession): super().__init__(session, models.Visit)
class TerritoryService(TenantCrudService):
    def __init__(self, session: AsyncSession): super().__init__(session, models.Territory)
class ProductService(TenantCrudService):
    def __init__(self, session: AsyncSession): super().__init__(session, models.Product)
class RouteService(TenantCrudService):
    def __init__(self, session: AsyncSession): super().__init__(session, models.Route)
class CampaignService(TenantCrudService):
    def __init__(self, session: AsyncSession): super().__init__(session, models.Campaign)
class NotificationService(TenantCrudService):
    def __init__(self, session: AsyncSession): super().__init__(session, models.Notification)
    async def list_for_user(self, organization_id, user_id, *, limit, offset, sort, search):
        statement = self.repo.tenant_query(organization_id).where(models.Notification.user_id == user_id)
        if search:
            from sqlalchemy import or_
            statement = statement.where(or_(
                models.Notification.title.ilike(f"%{search}%"),
                models.Notification.body.ilike(f"%{search}%"),
                models.Notification.notification_type.ilike(f"%{search}%"),
            ))
        sort_column = getattr(models.Notification, sort.lstrip("-"), models.Notification.created_at)
        statement = statement.order_by(
            sort_column.desc() if sort.startswith("-") else sort_column.asc()
        ).limit(limit).offset(offset)
        return list((await self.session.scalars(statement)).all())
class CalendarService(TenantCrudService):
    def __init__(self, session: AsyncSession): super().__init__(session, models.CalendarEvent)
