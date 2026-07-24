from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.business import TerritoryCreate
from app.services.business_services import CalendarService, CampaignService, DoctorService, NotificationService, ProductService, RouteService, TerritoryService, VisitService
from app.services.crud import TenantCrudService
from app.services.priority import PriorityCalculationEngine
from app.domain import models

class ServiceToolKit:
    def __init__(self, session: AsyncSession, organization_id: UUID): self.session=session; self.organization_id=organization_id
    async def doctor_search(self, query: str, limit: int = 10): return await DoctorService(self.session).list(self.organization_id, limit=limit, offset=0, sort="last_name", search=query)
    async def visit_history(self, doctor_id: UUID): return [v for v in await VisitService(self.session).list(self.organization_id, limit=50, offset=0, sort="-scheduled_at", search=None) if v.hcp_id == doctor_id]
    async def doctor_timeline(self, doctor_id: UUID): return await self.visit_history(doctor_id)
    async def products(self, search: str | None = None): return await ProductService(self.session).list(self.organization_id, limit=25, offset=0, sort="name", search=search)
    async def campaigns(self, search: str | None = None): return await CampaignService(self.session).list(self.organization_id, limit=25, offset=0, sort="name", search=search)
    async def routes(self, search: str | None = None): return await RouteService(self.session).list(self.organization_id, limit=25, offset=0, sort="route_date", search=search)
    async def calendar(self, search: str | None = None): return await CalendarService(self.session).list(self.organization_id, limit=25, offset=0, sort="starts_at", search=search)
    async def notifications(self, search: str | None = None): return await NotificationService(self.session).list(self.organization_id, limit=25, offset=0, sort="-created_at", search=search)
    async def priority(self, doctor_id: UUID): return await PriorityCalculationEngine().calculate(self.session, self.organization_id, doctor_id)
    async def recommendations(self, doctor_id: UUID): return [r for r in await TenantCrudService(self.session, models.Recommendation).list(self.organization_id, limit=25, offset=0, sort="-score", search=None) if r.hcp_id == doctor_id]
