from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import require_permissions
from app.infrastructure.database.session import get_session
from app.schemas.auth import UserMe
from app.schemas.operations import CalendarRangeRequest, RouteCreateRequest, RouteUpdateRequest, VisitCreateRequest, VisitNoteRequest, VisitUpdateRequest
from app.services.operations import CalendarService, RoutePlanningService, VisitManagementService

router = APIRouter(tags=["Field Operations"])

@router.post("/visits", status_code=status.HTTP_201_CREATED)
async def create_visit(payload: VisitCreateRequest, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("visits:write"))):
    return await VisitManagementService(session).create(user.organization_id, user.id, payload)
@router.patch("/visits/{visit_id}")
async def update_visit(visit_id: UUID, payload: VisitUpdateRequest, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("visits:write"))):
    return await VisitManagementService(session).update(user.organization_id, visit_id, payload)
@router.delete("/visits/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_visit(visit_id: UUID, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("visits:write"))):
    await VisitManagementService(session).delete(user.organization_id, visit_id)
@router.post("/visits/{visit_id}/notes", status_code=status.HTTP_201_CREATED)
async def add_visit_note(visit_id: UUID, payload: VisitNoteRequest, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("visits:write"))):
    return await VisitManagementService(session).add_note(user.organization_id, visit_id, user.id, payload)
@router.get("/visits/{visit_id}/timeline")
async def visit_timeline(visit_id: UUID, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("visits:read"))):
    return await VisitManagementService(session).timeline(user.organization_id, visit_id)

@router.post("/routes", status_code=status.HTTP_201_CREATED)
async def create_route(payload: RouteCreateRequest, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("routes:write"))):
    return await RoutePlanningService(session).create(user.organization_id, user.id, payload)
@router.patch("/routes/{route_id}")
async def update_route(route_id: UUID, payload: RouteUpdateRequest, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("routes:write"))):
    return await RoutePlanningService(session).update(user.organization_id, route_id, payload)
@router.post("/routes/{route_id}/optimize")
async def optimize_route(route_id: UUID, session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("routes:write"))):
    return await RoutePlanningService(session).optimize(user.organization_id, route_id)

@router.get("/calendar")
async def calendar(starts_at: datetime = Query(), ends_at: datetime = Query(), session: AsyncSession = Depends(get_session), user: UserMe = Depends(require_permissions("calendar:read"))):
    validated = CalendarRangeRequest(starts_at=starts_at, ends_at=ends_at)
    return await CalendarService(session).events(user.organization_id, user.id, validated.starts_at, validated.ends_at)
