from sqlalchemy import Select, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain import models
from app.infrastructure.repositories.generic import GenericRepository

class TenantRepository(GenericRepository):
    search_fields: tuple[str, ...] = ()
    def __init__(self, session: AsyncSession, model): super().__init__(session, model)
    def tenant_query(self, organization_id) -> Select:
        return self.query().where(self.model.organization_id == organization_id)
    async def list_for_tenant(self, organization_id, *, limit=50, offset=0, sort="created_at", search=None):
        stmt = self.tenant_query(organization_id)
        if search and self.search_fields:
            stmt = stmt.where(or_(*[getattr(self.model, f).ilike(f"%{search}%") for f in self.search_fields]))
        sort_col = getattr(self.model, sort.lstrip("-"), self.model.created_at)
        stmt = stmt.order_by(sort_col.desc() if sort.startswith("-") else sort_col.asc()).limit(limit).offset(offset)
        return list((await self.session.scalars(stmt)).all())
    async def get_for_tenant(self, organization_id, entity_id):
        return await self.session.scalar(self.tenant_query(organization_id).where(self.model.id == entity_id))

class RegionRepository(TenantRepository): search_fields=("name","code")
class TerritoryRepository(TenantRepository): search_fields=("name","code")
class SpecialtyRepository(TenantRepository): search_fields=("name",)
class HCPRepository(TenantRepository): search_fields=("first_name","last_name","npi","email")
class AddressRepository(TenantRepository): search_fields=("line1","city","state","postal_code")
class VisitRepository(TenantRepository): search_fields=("status","outcome")
class VisitNoteRepository(TenantRepository): search_fields=("content","note_type")
class ProductRepository(TenantRepository): search_fields=("name","sku")
class ProductCategoryRepository(TenantRepository): search_fields=("name",)
class ProductPriorityRuleRepository(TenantRepository): pass
class CampaignRepository(TenantRepository): search_fields=("name",)
class CallObjectiveRepository(TenantRepository): search_fields=("title","status")
class RecommendationRepository(TenantRepository): search_fields=("title","rationale","status")
class InteractionRepository(TenantRepository): search_fields=("channel","summary","sentiment")
class RouteRepository(TenantRepository): search_fields=("name","status")
class RouteStopRepository(TenantRepository): pass
class CalendarEventRepository(TenantRepository): search_fields=("title","event_type")
class ActivityRepository(TenantRepository): search_fields=("entity_type","action","description")
class AttachmentRepository(TenantRepository): search_fields=("file_name","content_type","storage_key")
class NotificationRepository(TenantRepository): search_fields=("title","body","notification_type")
class SettingsRepository(TenantRepository): search_fields=("scope","key")

REPOSITORY_BY_MODEL = {
    models.Region: RegionRepository, models.Territory: TerritoryRepository, models.Specialty: SpecialtyRepository, models.HCP: HCPRepository, models.Address: AddressRepository, models.Visit: VisitRepository, models.VisitNote: VisitNoteRepository, models.Product: ProductRepository, models.ProductCategory: ProductCategoryRepository, models.ProductPriorityRule: ProductPriorityRuleRepository, models.Campaign: CampaignRepository, models.CallObjective: CallObjectiveRepository, models.Recommendation: RecommendationRepository, models.Interaction: InteractionRepository, models.Route: RouteRepository, models.RouteStop: RouteStopRepository, models.CalendarEvent: CalendarEventRepository, models.Activity: ActivityRepository, models.Attachment: AttachmentRepository, models.Notification: NotificationRepository, models.Settings: SettingsRepository,
}
