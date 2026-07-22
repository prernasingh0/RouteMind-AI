from __future__ import annotations
from datetime import UTC, datetime
from math import asin, cos, radians, sin, sqrt
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models.business import Address, Attachment, CalendarEvent, HCP, Route, RouteStop, Visit, VisitNote
from app.schemas.operations import RouteCreateRequest, RouteUpdateRequest, VisitCreateRequest, VisitNoteRequest, VisitUpdateRequest


def not_found(resource: str) -> HTTPException:
    return HTTPException(status.HTTP_404_NOT_FOUND, f"{resource} not found")

class VisitManagementService:
    def __init__(self, session: AsyncSession): self.session = session
    async def _visit(self, organization_id: UUID, visit_id: UUID) -> Visit:
        visit = await self.session.scalar(select(Visit).where(Visit.id == visit_id, Visit.organization_id == organization_id, Visit.deleted_at.is_(None)))
        if visit is None: raise not_found("Visit")
        return visit
    async def create(self, organization_id: UUID, user_id: UUID, payload: VisitCreateRequest) -> Visit:
        doctor = await self.session.scalar(select(HCP.id).where(HCP.id == payload.hcp_id, HCP.organization_id == organization_id, HCP.deleted_at.is_(None)))
        if doctor is None: raise not_found("Doctor")
        visit = Visit(organization_id=organization_id, user_id=user_id, **payload.model_dump())
        self.session.add(visit); await self.session.commit(); await self.session.refresh(visit); return visit
    async def update(self, organization_id: UUID, visit_id: UUID, payload: VisitUpdateRequest) -> Visit:
        visit = await self._visit(organization_id, visit_id)
        for key, value in payload.model_dump(exclude_unset=True).items(): setattr(visit, key, value)
        if visit.status == "completed" and visit.completed_at is None: visit.completed_at = datetime.now(UTC)
        self.session.add(visit); await self.session.commit(); await self.session.refresh(visit); return visit
    async def delete(self, organization_id: UUID, visit_id: UUID) -> None:
        visit = await self._visit(organization_id, visit_id); visit.mark_deleted(); await self.session.commit()
    async def add_note(self, organization_id: UUID, visit_id: UUID, user_id: UUID, payload: VisitNoteRequest) -> VisitNote:
        await self._visit(organization_id, visit_id)
        note = VisitNote(organization_id=organization_id, visit_id=visit_id, author_user_id=user_id, **payload.model_dump())
        self.session.add(note); await self.session.commit(); await self.session.refresh(note); return note
    async def timeline(self, organization_id: UUID, visit_id: UUID) -> dict:
        visit = await self._visit(organization_id, visit_id)
        notes = (await self.session.scalars(select(VisitNote).where(VisitNote.organization_id == organization_id, VisitNote.visit_id == visit_id, VisitNote.deleted_at.is_(None)).order_by(VisitNote.created_at))).all()
        attachments = (await self.session.scalars(select(Attachment).where(Attachment.organization_id == organization_id, Attachment.entity_type == "visit", Attachment.entity_id == visit_id, Attachment.deleted_at.is_(None)))).all()
        return {"visit": visit, "notes": notes, "attachments": attachments}
    async def apply_postcall(self, organization_id: UUID, visit_id: UUID, outcome: str, follow_up_at: datetime | None) -> Visit:
        return await self.update(organization_id, visit_id, VisitUpdateRequest(status="completed", outcome=outcome, follow_up_at=follow_up_at))

class DistanceCalculator:
    """Provider-neutral geodesic distance calculator for route planning."""
    def kilometers(self, origin: tuple[float, float], destination: tuple[float, float]) -> float:
        lat1, lon1, lat2, lon2 = map(radians, (*origin, *destination)); dlat, dlon = lat2-lat1, lon2-lon1
        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        return 6371.0088 * 2 * asin(sqrt(a))

class RoutePlanningService:
    def __init__(self, session: AsyncSession, distance: DistanceCalculator | None = None): self.session = session; self.distance = distance or DistanceCalculator()
    async def _route(self, organization_id: UUID, route_id: UUID) -> Route:
        route = await self.session.scalar(select(Route).where(Route.id == route_id, Route.organization_id == organization_id, Route.deleted_at.is_(None)))
        if route is None: raise not_found("Route")
        return route
    async def create(self, organization_id: UUID, user_id: UUID, payload: RouteCreateRequest) -> Route:
        doctor_ids = [stop.hcp_id for stop in payload.stops]
        if doctor_ids:
            matched = (await self.session.scalars(select(HCP.id).where(HCP.id.in_(doctor_ids), HCP.organization_id == organization_id, HCP.deleted_at.is_(None)))).all()
            if len(set(matched)) != len(set(doctor_ids)):
                raise not_found("Doctor")
        route = Route(organization_id=organization_id, user_id=user_id, name=payload.name, route_date=payload.route_date)
        self.session.add(route); await self.session.flush()
        for sequence, stop in enumerate(payload.stops, start=1): self.session.add(RouteStop(organization_id=organization_id, route_id=route.id, sequence=sequence, **stop.model_dump()))
        await self.session.commit(); await self.session.refresh(route); return route
    async def update(self, organization_id: UUID, route_id: UUID, payload: RouteUpdateRequest) -> Route:
        route = await self._route(organization_id, route_id)
        for key, value in payload.model_dump(exclude_unset=True).items(): setattr(route, key, value)
        await self.session.commit(); await self.session.refresh(route); return route
    async def optimize(self, organization_id: UUID, route_id: UUID) -> dict:
        route = await self._route(organization_id, route_id)
        stops = list((await self.session.scalars(select(RouteStop).where(RouteStop.route_id == route_id, RouteStop.organization_id == organization_id, RouteStop.deleted_at.is_(None)))).all())
        coordinates: dict[UUID, tuple[float, float]] = {}
        for stop in stops:
            address = await self.session.scalar(select(Address).where(Address.hcp_id == stop.hcp_id, Address.organization_id == organization_id, Address.deleted_at.is_(None), Address.latitude.is_not(None), Address.longitude.is_not(None)).order_by(Address.created_at))
            if address: coordinates[stop.hcp_id] = (address.latitude, address.longitude)
        # deterministic nearest-neighbour ordering; stops without coordinates retain their original order last.
        ordered, remaining, current = [], stops[:], None
        while remaining:
            candidates = [s for s in remaining if s.hcp_id in coordinates]
            if not candidates: ordered.extend(remaining); break
            selected = min(candidates, key=lambda s: 0 if current is None else self.distance.kilometers(current, coordinates[s.hcp_id]))
            ordered.append(selected); remaining.remove(selected); current = coordinates[selected.hcp_id]
        total = 0.0; prior = None
        for sequence, stop in enumerate(ordered, start=1):
            stop.sequence = sequence
            point = coordinates.get(stop.hcp_id)
            if prior and point: total += self.distance.kilometers(prior, point); stop.travel_minutes = max(1, round(self.distance.kilometers(prior, point) / 40 * 60))
            else: stop.travel_minutes = 0
            prior = point or prior
        route.status = "optimized"; await self.session.commit()
        return {"route": route, "stops": ordered, "distance_km": round(total, 2), "coordinates_available": len(coordinates), "map_stops": [{"hcp_id": str(stop.hcp_id), "sequence": stop.sequence, "latitude": coordinates.get(stop.hcp_id, (None, None))[0], "longitude": coordinates.get(stop.hcp_id, (None, None))[1]} for stop in ordered]}

class CalendarService:
    def __init__(self, session: AsyncSession): self.session = session
    async def events(self, organization_id: UUID, user_id: UUID, starts_at: datetime, ends_at: datetime) -> list[dict]:
        visits = (await self.session.scalars(select(Visit).where(Visit.organization_id == organization_id, Visit.user_id == user_id, Visit.scheduled_at >= starts_at, Visit.scheduled_at < ends_at, Visit.deleted_at.is_(None)))).all()
        events = (await self.session.scalars(select(CalendarEvent).where(CalendarEvent.organization_id == organization_id, CalendarEvent.user_id == user_id, CalendarEvent.starts_at >= starts_at, CalendarEvent.starts_at < ends_at, CalendarEvent.deleted_at.is_(None)))).all()
        return ([{"id": str(v.id), "type": "visit", "title": "Scheduled doctor visit", "starts_at": v.scheduled_at, "ends_at": v.follow_up_at or v.scheduled_at, "hcp_id": str(v.hcp_id), "status": v.status} for v in visits] + [{"id": str(e.id), "type": e.event_type, "title": e.title, "starts_at": e.starts_at, "ends_at": e.ends_at, "hcp_id": str(e.hcp_id) if e.hcp_id else None} for e in events])
