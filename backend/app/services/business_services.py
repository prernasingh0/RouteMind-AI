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
class CalendarService(TenantCrudService):
    def __init__(self, session: AsyncSession): super().__init__(session, models.CalendarEvent)
