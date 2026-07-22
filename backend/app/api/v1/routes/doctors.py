from uuid import UUID
from fastapi import APIRouter, Depends, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import io
from app.api.dependencies import require_permissions
from app.infrastructure.database.session import get_session
from app.schemas.auth import UserMe
from app.schemas.business import HCPCreate, HCPRead, HCPUpdate
from app.schemas.doctors import BulkDoctorOperation, DoctorPrioritySimulation, DoctorProfile, DoctorSearchParams, TimelineItem
from app.services.doctor_management import DoctorManagementService

router = APIRouter(prefix="/doctors", tags=["Doctor Management"])

@router.get("/search", response_model=list[HCPRead])
async def search_doctors(limit:int=Query(25,ge=1,le=200), offset:int=Query(0,ge=0), sort:str="last_name", search:str|None=None, territory_id:UUID|None=None, region_id:UUID|None=None, specialty_id:UUID|None=None, status_filter:str|None=Query(None, alias="status"), tag:str|None=None, session:AsyncSession=Depends(get_session), user:UserMe=Depends(require_permissions("doctors:read"))):
    return await DoctorManagementService(session).search(user.organization_id, DoctorSearchParams(limit=limit, offset=offset, sort=sort, search=search, territory_id=territory_id, region_id=region_id, specialty_id=specialty_id, status=status_filter, tag=tag))
@router.post("", response_model=HCPRead, status_code=status.HTTP_201_CREATED)
async def create_doctor(payload:HCPCreate, session:AsyncSession=Depends(get_session), user:UserMe=Depends(require_permissions("doctors:write"))): return await DoctorManagementService(session).create(user.organization_id, payload)
@router.patch("/{doctor_id}", response_model=HCPRead)
async def update_doctor(doctor_id:UUID, payload:HCPUpdate, session:AsyncSession=Depends(get_session), user:UserMe=Depends(require_permissions("doctors:write"))): return await DoctorManagementService(session).update(user.organization_id, doctor_id, payload)
@router.delete("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_doctor(doctor_id:UUID, session:AsyncSession=Depends(get_session), user:UserMe=Depends(require_permissions("doctors:write"))): await DoctorManagementService(session).delete(user.organization_id, doctor_id)
@router.post("/bulk")
async def bulk_doctors(payload:BulkDoctorOperation, session:AsyncSession=Depends(get_session), user:UserMe=Depends(require_permissions("doctors:write"))): return await DoctorManagementService(session).bulk(user.organization_id, payload)
@router.post("/import")
async def import_doctors(file:UploadFile, session:AsyncSession=Depends(get_session), user:UserMe=Depends(require_permissions("doctors:write"))): return await DoctorManagementService(session).import_csv(user.organization_id, file)
@router.get("/export")
async def export_doctors(session:AsyncSession=Depends(get_session), user:UserMe=Depends(require_permissions("doctors:read"))): return StreamingResponse(io.BytesIO((await DoctorManagementService(session).export_csv(user.organization_id)).encode()), media_type="text/csv", headers={"Content-Disposition":"attachment; filename=doctors.csv"})
@router.get("/{doctor_id}/profile", response_model=DoctorProfile)
async def doctor_profile(doctor_id:UUID, session:AsyncSession=Depends(get_session), user:UserMe=Depends(require_permissions("doctors:read"))): return await DoctorManagementService(session).profile(user.organization_id, doctor_id)
@router.get("/{doctor_id}/timeline", response_model=list[TimelineItem])
async def doctor_timeline(doctor_id:UUID, session:AsyncSession=Depends(get_session), user:UserMe=Depends(require_permissions("doctors:read"))): return await DoctorManagementService(session).timeline(user.organization_id, doctor_id)
@router.get("/{doctor_id}/priority/history")
async def priority_history(doctor_id:UUID, session:AsyncSession=Depends(get_session), user:UserMe=Depends(require_permissions("doctors:read"))): return await DoctorManagementService(session).priority_history(user.organization_id, doctor_id)
@router.post("/{doctor_id}/priority/simulate")
async def simulate_priority(doctor_id:UUID, payload:DoctorPrioritySimulation, session:AsyncSession=Depends(get_session), user:UserMe=Depends(require_permissions("doctors:read"))): return await DoctorManagementService(session).simulate_priority(user.organization_id, doctor_id, payload)
