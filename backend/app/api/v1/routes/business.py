from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_current_user, require_permissions
from app.domain import models
from app.infrastructure.database.session import get_session
from app.schemas.auth import UserMe
from app.schemas import business as s
from app.services.crud import TenantCrudService
from app.services.business_services import CalendarService, CampaignService, DoctorService, NotificationService, ProductService, RouteService, TerritoryService, VisitService
from app.services.priority import PriorityCalculationEngine
from app.services.doctor_management import DoctorManagementService

router = APIRouter(tags=["Business Domain"])

def register_crud(path: str, model: Any, create_schema: Any, update_schema: Any, read_schema: Any, permission_prefix: str, service_cls: Any = TenantCrudService) -> None:
    def service(session: AsyncSession):
        return service_cls(session) if service_cls is not TenantCrudService else TenantCrudService(session, model)
    async def list_items(limit: int = Query(50, ge=1, le=200), offset: int = Query(0, ge=0), sort: str = "created_at", search: str | None = None, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions(f"{permission_prefix}:read"))):
        return await service(session).list(user.organization_id, limit=limit, offset=offset, sort=sort, search=search)
    async def create_item(payload: create_schema, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions(f"{permission_prefix}:write"))):
        return await service(session).create(user.organization_id, payload)
    async def get_item(item_id: UUID, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions(f"{permission_prefix}:read"))):
        return await service(session).get(user.organization_id, item_id)
    async def update_item(item_id: UUID, payload: update_schema, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions(f"{permission_prefix}:write"))):
        return await service(session).update(user.organization_id, item_id, payload)
    async def delete_item(item_id: UUID, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions(f"{permission_prefix}:write"))):
        await service(session).delete(user.organization_id, item_id)
    router.add_api_route(path, list_items, methods=["GET"], response_model=list[read_schema])
    router.add_api_route(path, create_item, methods=["POST"], status_code=status.HTTP_201_CREATED, response_model=read_schema)
    router.add_api_route(path + "/{item_id}", get_item, methods=["GET"], response_model=read_schema)
    router.add_api_route(path + "/{item_id}", update_item, methods=["PATCH"], response_model=read_schema)
    router.add_api_route(path + "/{item_id}", delete_item, methods=["DELETE"], status_code=status.HTTP_204_NO_CONTENT)

register_crud("/regions", models.Region, s.RegionCreate, s.RegionUpdate, s.RegionRead, "territories")
register_crud("/territories", models.Territory, s.TerritoryCreate, s.TerritoryUpdate, s.TerritoryRead, "territories", TerritoryService)
register_crud("/specialties", models.Specialty, s.SpecialtyCreate, s.SpecialtyUpdate, s.SpecialtyRead, "doctors")
register_crud("/doctors", models.HCP, s.HCPCreate, s.HCPUpdate, s.HCPRead, "doctors", DoctorService)
register_crud("/addresses", models.Address, s.AddressCreate, s.AddressUpdate, s.AddressRead, "doctors")
register_crud("/product-categories", models.ProductCategory, s.ProductCategoryCreate, s.ProductCategoryUpdate, s.ProductCategoryRead, "products")
register_crud("/products", models.Product, s.ProductCreate, s.ProductUpdate, s.ProductRead, "products", ProductService)
register_crud("/product-priority-rules", models.ProductPriorityRule, s.ProductPriorityRuleCreate, s.ProductPriorityRuleUpdate, s.ProductPriorityRuleRead, "products")
register_crud("/campaigns", models.Campaign, s.CampaignCreate, s.CampaignUpdate, s.CampaignRead, "campaigns", CampaignService)
register_crud("/visits", models.Visit, s.VisitCreate, s.VisitUpdate, s.VisitRead, "visits", VisitService)
register_crud("/visit-notes", models.VisitNote, s.VisitNoteCreate, s.VisitNoteUpdate, s.VisitNoteRead, "visits")
register_crud("/call-objectives", models.CallObjective, s.CallObjectiveCreate, s.CallObjectiveUpdate, s.CallObjectiveRead, "visits")
register_crud("/recommendations", models.Recommendation, s.RecommendationCreate, s.RecommendationUpdate, s.RecommendationRead, "doctors")
register_crud("/interactions", models.Interaction, s.InteractionCreate, s.InteractionUpdate, s.InteractionRead, "doctors")
register_crud("/routes", models.Route, s.RouteCreate, s.RouteUpdate, s.RouteRead, "routes", RouteService)
register_crud("/route-stops", models.RouteStop, s.RouteStopCreate, s.RouteStopUpdate, s.RouteStopRead, "routes")
register_crud("/calendar-events", models.CalendarEvent, s.CalendarEventCreate, s.CalendarEventUpdate, s.CalendarEventRead, "calendar", CalendarService)
register_crud("/activities", models.Activity, s.ActivityCreate, s.ActivityUpdate, s.ActivityRead, "activities")
register_crud("/attachments", models.Attachment, s.AttachmentCreate, s.AttachmentUpdate, s.AttachmentRead, "attachments")
register_crud("/notifications", models.Notification, s.NotificationCreate, s.NotificationUpdate, s.NotificationRead, "notifications", NotificationService)
register_crud("/settings", models.Settings, s.SettingsCreate, s.SettingsUpdate, s.SettingsRead, "settings")

@router.get("/doctors/{doctor_id}/priority", response_model=s.PriorityBreakdown)
async def doctor_priority(doctor_id: UUID, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("doctors:read"))):
    return await DoctorManagementService(session).snapshot_priority(user.organization_id, doctor_id)
