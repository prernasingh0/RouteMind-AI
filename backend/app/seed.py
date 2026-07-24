"""Idempotent development/demo data bootstrap.

Run after migrations with ``python -m app.seed``. Production deployments should
use their own provisioning process and must not run this command.
"""

import asyncio
from datetime import date, datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain.models import (
    Address, HCP, Notification, Organization, Permission, Product, Region, Role, RolePermission,
    Route, RouteStop, Territory, User, Visit,
)
from app.infrastructure.database.session import AsyncSessionFactory, engine
from app.infrastructure.security.passwords import hash_password

DEMO_EMAIL = "rep@acme.com"
DEMO_PASSWORD = "CorrectHorse1"
PERMISSIONS = {
    f"{area}:{action}"
    for area in ("territories", "doctors", "products", "campaigns", "visits", "routes", "calendar", "activities", "attachments", "notifications", "settings")
    for action in ("read", "write")
} | {"ai:use", "users:read"}


async def seed() -> None:
    async with AsyncSessionFactory() as session:
        organization = await session.scalar(select(Organization).where(Organization.slug == "acme"))
        if organization is None:
            organization = Organization(name="Acme Pharma", slug="acme", status="active", settings={})
            session.add(organization)
            await session.flush()

        role = await session.scalar(select(Role).options(selectinload(Role.permissions)).where(Role.organization_id == organization.id, Role.name == "Demo Representative"))
        if role is None:
            role = Role(organization_id=organization.id, name="Demo Representative", description="Local development account")
            session.add(role)
            await session.flush()

        permissions = []
        for code in sorted(PERMISSIONS):
            permission = await session.scalar(select(Permission).where(Permission.code == code))
            if permission is None:
                permission = Permission(code=code, description=f"{code} permission")
                session.add(permission)
                await session.flush()
            permissions.append(permission)
        # Write join rows directly; replacing a many-to-many collection can
        # trigger an implicit lazy load under async SQLAlchemy.
        existing_permission_ids = set((await session.scalars(select(RolePermission.permission_id).where(RolePermission.role_id == role.id))).all())
        for permission in permissions:
            if permission.id not in existing_permission_ids:
                session.add(RolePermission(role_id=role.id, permission_id=permission.id))

        user = await session.scalar(select(User).options(selectinload(User.roles)).where(User.organization_id == organization.id, User.email == DEMO_EMAIL))
        if user is None:
            user = User(organization_id=organization.id, email=DEMO_EMAIL, full_name="Demo Representative", hashed_password=hash_password(DEMO_PASSWORD), roles=[role])
            session.add(user)
            await session.flush()
        elif role not in user.roles:
            user.roles.append(role)
        # Existing local accounts should also be able to use the seeded dashboard.
        for existing_user in (await session.scalars(select(User).options(selectinload(User.roles)).where(User.organization_id == organization.id))).all():
            if role not in existing_user.roles:
                existing_user.roles.append(role)

        region = await session.scalar(select(Region).where(Region.organization_id == organization.id, Region.name == "Northeast"))
        if region is None:
            region = Region(organization_id=organization.id, name="Northeast", code="NE")
            session.add(region)
            await session.flush()
        territory = await session.scalar(select(Territory).where(Territory.organization_id == organization.id, Territory.name == "New York"))
        if territory is None:
            territory = Territory(organization_id=organization.id, region_id=region.id, name="New York", code="NY", target_visits_per_month=24)
            session.add(territory)
            await session.flush()

        doctor = await session.scalar(select(HCP).where(HCP.organization_id == organization.id, HCP.npi == "1000000001"))
        if doctor is None:
            doctor = HCP(organization_id=organization.id, territory_id=territory.id, first_name="Maya", last_name="Patel", npi="1000000001", email="maya.patel@example.com", phone="212-555-0101", engagement_score=72, prescription_trend=18)
            session.add(doctor)
            await session.flush()
            session.add(Address(organization_id=organization.id, hcp_id=doctor.id, line1="100 Madison Avenue", city="New York", state="NY", postal_code="10016", latitude=40.745, longitude=-73.984))

        # A small, varied HCP panel makes the planning workflow demonstrable.
        sample_hcps = [
            ("James", "Chen", "1000000002", "200 Park Avenue", 40.754, -73.984, 88, 30),
            ("Elena", "Garcia", "1000000003", "55 Water Street", 40.704, -74.011, 64, 12),
            ("Robert", "Williams", "1000000004", "425 Lexington Avenue", 40.751, -73.975, 47, -5),
            ("Aisha", "Johnson", "1000000005", "1 Penn Plaza", 40.750, -73.993, 76, 22),
            ("Michael", "Brown", "1000000006", "30 Hudson Street", 40.714, -74.016, 39, -12),
            ("Sofia", "Martinez", "1000000007", "10 Union Square", 40.735, -73.990, 91, 35),
            ("Daniel", "Kim", "1000000008", "500 Fifth Avenue", 40.762, -73.977, 58, 8),
        ]
        for first_name, last_name, npi, line1, latitude, longitude, engagement, trend in sample_hcps:
            sample_doctor = await session.scalar(select(HCP).where(HCP.organization_id == organization.id, HCP.npi == npi))
            if sample_doctor is None:
                sample_doctor = HCP(organization_id=organization.id, territory_id=territory.id, first_name=first_name, last_name=last_name, npi=npi, email=f"{first_name.lower()}.{last_name.lower()}@example.com", status="active", engagement_score=engagement, prescription_trend=trend)
                session.add(sample_doctor)
                await session.flush()
                session.add(Address(organization_id=organization.id, hcp_id=sample_doctor.id, line1=line1, city="New York", state="NY", postal_code="10001", latitude=latitude, longitude=longitude))
            if await session.scalar(select(Visit.id).where(Visit.organization_id == organization.id, Visit.hcp_id == sample_doctor.id)) is None:
                session.add(Visit(organization_id=organization.id, hcp_id=sample_doctor.id, user_id=user.id, scheduled_at=datetime.now(timezone.utc) + timedelta(days=2), status="scheduled"))

        visit = await session.scalar(select(Visit).where(Visit.organization_id == organization.id, Visit.hcp_id == doctor.id))
        if visit is None:
            visit = Visit(organization_id=organization.id, hcp_id=doctor.id, user_id=user.id, scheduled_at=datetime.now(timezone.utc) + timedelta(days=1, hours=2), status="scheduled")
            session.add(visit)

        if await session.scalar(select(Notification).where(Notification.organization_id == organization.id, Notification.user_id == user.id, Notification.title == "Demo data is ready")) is None:
            session.add(Notification(organization_id=organization.id, user_id=user.id, title="Demo data is ready", body="Your seeded doctor, visit, and route data is ready to explore.", notification_type="system", metadata_={}))

        await session.flush()
        route = await session.scalar(select(Route).where(Route.organization_id == organization.id, Route.name == "Northeast Demo Route"))
        if route is None:
            route = Route(organization_id=organization.id, user_id=user.id, name="Northeast Demo Route", route_date=date.today(), status="draft")
            session.add(route)
            await session.flush()
            session.add(RouteStop(organization_id=organization.id, route_id=route.id, hcp_id=doctor.id, sequence=1))
        existing_stop_ids = set((await session.scalars(select(RouteStop.hcp_id).where(RouteStop.route_id == route.id, RouteStop.deleted_at.is_(None)))).all())
        all_doctors = (await session.scalars(select(HCP).where(HCP.organization_id == organization.id, HCP.deleted_at.is_(None)).order_by(HCP.last_name))).all()
        next_sequence = len(existing_stop_ids) + 1
        for candidate in all_doctors:
            if candidate.id not in existing_stop_ids:
                session.add(RouteStop(organization_id=organization.id, route_id=route.id, hcp_id=candidate.id, sequence=next_sequence))
                next_sequence += 1

        await session.commit()
        print(f"Seeded {organization.slug}; login {DEMO_EMAIL} / {DEMO_PASSWORD}")


async def main() -> None:
    await seed()
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
