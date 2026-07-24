import pytest
from app.domain.models import HCP, Organization, Territory, User
from app.infrastructure.security.passwords import hash_password
from app.schemas.business import HCPCreate
from app.schemas.doctors import DoctorPrioritySimulation, DoctorSearchParams
from app.services.doctor_management import DoctorManagementService

@pytest.mark.asyncio
async def test_doctor_profile_timeline_priority_and_bulk(session_factory):
    async with session_factory() as session:
        org=Organization(name="Doctor Org", slug="doctor-org", status="active", settings={}); user=User(organization=org,email="doc@test.dev",full_name="Doc",hashed_password=hash_password("CorrectHorse1")); session.add(user); await session.commit(); await session.refresh(org); await session.refresh(user)
        territory=Territory(organization_id=org.id,name="Central",target_visits_per_month=20); session.add(territory); await session.commit(); await session.refresh(territory)
        service=DoctorManagementService(session); doctor=await service.create(org.id, HCPCreate(territory_id=territory.id, first_name="Maya", last_name="Patel", status="active"))
        assert (await service.search(org.id, DoctorSearchParams(search="Patel")))[0].id == doctor.id
        profile=await service.profile(org.id, doctor.id); assert profile.doctor.id == doctor.id and profile.current_priority.total_score >= 0
        await service.snapshot_priority(org.id, doctor.id); assert len(await service.priority_history(org.id, doctor.id)) == 1
        simulated=await service.simulate_priority(org.id, doctor.id, DoctorPrioritySimulation(manager_adjustment=12)); assert simulated["simulated"]["factors"]["manager_adjustments"] == 12
        result=await service.bulk(org.id, type("Bulk", (), {"doctor_ids":[doctor.id], "operation":"deactivate", "value":None})()); assert result["updated"] == 1
