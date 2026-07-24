from datetime import datetime, timedelta, timezone
import pytest
from app.domain.models import Campaign, HCP, Organization, Permission, Product, ProductPriorityRule, Role, Territory, User, Visit
from app.infrastructure.security.passwords import hash_password
from app.schemas.business import HCPCreate, TerritoryCreate
from app.services.business_services import DoctorService, TerritoryService
from app.services.priority import PriorityCalculationEngine

@pytest.mark.asyncio
async def test_tenant_crud_soft_delete_and_search(session_factory):
    async with session_factory() as session:
        org = Organization(name="Domain Org", slug="domain", status="active", settings={})
        session.add(org); await session.commit(); await session.refresh(org)
        territory = await TerritoryService(session).create(org.id, TerritoryCreate(name="North", code="N1"))
        found = await TerritoryService(session).list(org.id, limit=10, offset=0, sort="name", search="Nor")
        assert found[0].id == territory.id
        await TerritoryService(session).delete(org.id, territory.id)
        assert await TerritoryService(session).list(org.id, limit=10, offset=0, sort="name", search="Nor") == []

@pytest.mark.asyncio
async def test_tenant_isolation_in_services(session_factory):
    async with session_factory() as session:
        org1 = Organization(name="Tenant One", slug="tenant-one", status="active", settings={})
        org2 = Organization(name="Tenant Two", slug="tenant-two", status="active", settings={})
        session.add_all([org1, org2]); await session.commit(); await session.refresh(org1); await session.refresh(org2)
        territory = await TerritoryService(session).create(org1.id, TerritoryCreate(name="Protected"))
        visible = await TerritoryService(session).list(org1.id, limit=10, offset=0, sort="created_at", search=None)
        hidden = await TerritoryService(session).list(org2.id, limit=10, offset=0, sort="created_at", search=None)
        assert territory.id in [item.id for item in visible]
        assert territory.id not in [item.id for item in hidden]

@pytest.mark.asyncio
async def test_priority_calculation_breakdown(session_factory):
    async with session_factory() as session:
        org = Organization(name="Priority Org", slug="priority", status="active", settings={})
        user = User(organization=org, email="manager@priority.test", full_name="Manager", hashed_password=hash_password("CorrectHorse1"))
        session.add(user); await session.commit(); await session.refresh(org); await session.refresh(user)
        territory = Territory(organization_id=org.id, name="Priority Territory", target_visits_per_month=30)
        session.add(territory); await session.commit(); await session.refresh(territory)
        doctor = HCP(organization_id=org.id, territory_id=territory.id, first_name="Ana", last_name="Smith", engagement_score=5, prescription_trend=4, manager_adjustment=6)
        product = Product(organization_id=org.id, name="CardioMax", priority_weight=3)
        campaign = Campaign(organization_id=org.id, product_id=None, name="Launch", weight=2, is_active=True)
        session.add_all([doctor, product, campaign]); await session.commit(); await session.refresh(doctor); await session.refresh(product)
        session.add_all([
            ProductPriorityRule(organization_id=org.id, product_id=product.id, territory_id=territory.id, weight=2, criteria={}),
            Visit(organization_id=org.id, hcp_id=doctor.id, user_id=user.id, scheduled_at=datetime.now(timezone.utc)-timedelta(days=40), completed_at=datetime.now(timezone.utc)-timedelta(days=40), status="completed"),
            Visit(organization_id=org.id, hcp_id=doctor.id, user_id=user.id, scheduled_at=datetime.now(timezone.utc)-timedelta(days=1), status="missed"),
        ])
        await session.commit()
        result = await PriorityCalculationEngine().calculate(session, org.id, doctor.id)
        assert result.total_score > 0
        assert set(result.factors) >= {"days_since_last_visit", "visit_frequency", "campaign_weight", "product_priority", "missed_visits", "manager_adjustments", "territory_targets"}

@pytest.mark.asyncio
async def test_authorization_requires_permissions(client):
    login = await client.post("/api/v1/auth/login", json={"organization_slug":"acme","email":"rep@acme.com","password":"CorrectHorse1"})
    response = await client.get("/api/v1/territories", headers={"Authorization": f"Bearer {login.json()['access_token']}"})
    assert response.status_code == 403
