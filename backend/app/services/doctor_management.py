import csv, io
from datetime import datetime, timezone
from uuid import UUID
from fastapi import HTTPException, UploadFile, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models import AIConversation, Attachment, Campaign, DoctorCampaignAssociation, DoctorPrioritySnapshot, DoctorProductAssociation, DoctorTag, HCP, Notification, Product, Recommendation, Region, Specialty, Territory, Visit, VisitNote
from app.schemas.business import HCPCreate, HCPUpdate
from app.schemas.doctors import BulkDoctorOperation, DoctorPrioritySimulation, DoctorProfile, DoctorSearchParams, PriorityHistoryItem, TimelineItem
from app.services.business_services import DoctorService
from app.services.priority import PriorityCalculationEngine

class DoctorManagementService:
    def __init__(self, session: AsyncSession): self.session=session
    async def search(self, organization_id: UUID, params: DoctorSearchParams):
        stmt = select(HCP).where(HCP.organization_id==organization_id, HCP.deleted_at.is_(None))
        if params.search: stmt = stmt.where(or_(HCP.first_name.ilike(f"%{params.search}%"), HCP.last_name.ilike(f"%{params.search}%"), HCP.npi.ilike(f"%{params.search}%"), HCP.email.ilike(f"%{params.search}%")))
        if params.territory_id: stmt = stmt.where(HCP.territory_id==params.territory_id)
        if params.specialty_id: stmt = stmt.where(HCP.specialty_id==params.specialty_id)
        if params.status: stmt = stmt.where(HCP.status==params.status)
        sort_col = getattr(HCP, params.sort.lstrip('-'), HCP.last_name); stmt = stmt.order_by(sort_col.desc() if params.sort.startswith('-') else sort_col.asc()).limit(params.limit).offset(params.offset)
        return list((await self.session.scalars(stmt)).all())
    async def create(self, organization_id: UUID, payload: HCPCreate): return await DoctorService(self.session).create(organization_id, payload)
    async def update(self, organization_id: UUID, doctor_id: UUID, payload: HCPUpdate): return await DoctorService(self.session).update(organization_id, doctor_id, payload)
    async def delete(self, organization_id: UUID, doctor_id: UUID): await DoctorService(self.session).delete(organization_id, doctor_id)
    async def bulk(self, organization_id: UUID, payload: BulkDoctorOperation):
        doctors = list((await self.session.scalars(select(HCP).where(HCP.organization_id==organization_id, HCP.id.in_(payload.doctor_ids), HCP.deleted_at.is_(None)))).all())
        for doctor in doctors:
            if payload.operation == 'deactivate': doctor.status='inactive'
            elif payload.operation == 'activate': doctor.status='active'
            elif payload.operation == 'assign_territory' and payload.value: doctor.territory_id=UUID(str(payload.value))
            else: raise HTTPException(status.HTTP_400_BAD_REQUEST, 'Unsupported bulk operation')
            self.session.add(doctor)
        await self.session.commit(); return {"updated": len(doctors)}
    async def profile(self, organization_id: UUID, doctor_id: UUID) -> DoctorProfile:
        doctor = await self.session.scalar(select(HCP).where(HCP.id==doctor_id, HCP.organization_id==organization_id, HCP.deleted_at.is_(None)))
        if not doctor: raise HTTPException(status.HTTP_404_NOT_FOUND, 'Doctor not found')
        territory = await self.session.get(Territory, doctor.territory_id); region = await self.session.get(Region, territory.region_id) if territory and territory.region_id else None
        visits = list((await self.session.scalars(select(Visit).where(Visit.organization_id==organization_id, Visit.hcp_id==doctor_id, Visit.deleted_at.is_(None)).order_by(Visit.scheduled_at.desc()).limit(20))).all())
        recommendations = list((await self.session.scalars(select(Recommendation).where(Recommendation.organization_id==organization_id, Recommendation.hcp_id==doctor_id, Recommendation.deleted_at.is_(None)).order_by(Recommendation.score.desc()))).all())
        product_links = list((await self.session.scalars(select(DoctorProductAssociation).where(DoctorProductAssociation.organization_id==organization_id, DoctorProductAssociation.hcp_id==doctor_id, DoctorProductAssociation.deleted_at.is_(None)))).all())
        campaign_links = list((await self.session.scalars(select(DoctorCampaignAssociation).where(DoctorCampaignAssociation.organization_id==organization_id, DoctorCampaignAssociation.hcp_id==doctor_id, DoctorCampaignAssociation.deleted_at.is_(None)))).all())
        tags = list((await self.session.scalars(select(DoctorTag).where(DoctorTag.organization_id==organization_id, DoctorTag.hcp_id==doctor_id, DoctorTag.deleted_at.is_(None)))).all())
        priority = await PriorityCalculationEngine().calculate(self.session, organization_id, doctor_id)
        return DoctorProfile(doctor=doctor, territory={"id": str(territory.id), "name": territory.name} if territory else None, region={"id": str(region.id), "name": region.name} if region else None, products=[{"product_id": str(p.product_id), "relationship_type": p.relationship_type, "strength": p.strength} for p in product_links], visit_history=[{"id": str(v.id), "scheduled_at": v.scheduled_at.isoformat(), "status": v.status, "outcome": v.outcome} for v in visits], campaigns=[{"campaign_id": str(c.campaign_id), "status": c.status} for c in campaign_links], recommendations=[{"id": str(r.id), "title": r.title, "score": r.score} for r in recommendations], current_priority=priority, recent_ai_interactions=[], tags=[t.name for t in tags])
    async def timeline(self, organization_id: UUID, doctor_id: UUID):
        items: list[TimelineItem] = []
        visits = list((await self.session.scalars(select(Visit).where(Visit.organization_id==organization_id, Visit.hcp_id==doctor_id, Visit.deleted_at.is_(None)))).all())
        for v in visits: items.append(TimelineItem(id=v.id, type='visit', occurred_at=v.completed_at or v.scheduled_at, title=f'Visit {v.status}', description=v.outcome or 'Scheduled visit', metadata={}))
        for n in (await self.session.scalars(select(VisitNote).where(VisitNote.organization_id==organization_id, VisitNote.deleted_at.is_(None)))).all(): items.append(TimelineItem(id=n.id, type='note', occurred_at=n.created_at, title=n.note_type, description=n.content, metadata={"visit_id": str(n.visit_id)}))
        for r in (await self.session.scalars(select(Recommendation).where(Recommendation.organization_id==organization_id, Recommendation.hcp_id==doctor_id, Recommendation.deleted_at.is_(None)))).all(): items.append(TimelineItem(id=r.id, type='recommendation', occurred_at=r.created_at, title=r.title, description=r.rationale, metadata={"score": r.score}))
        for a in (await self.session.scalars(select(Attachment).where(Attachment.organization_id==organization_id, Attachment.entity_type=='doctor', Attachment.entity_id==doctor_id, Attachment.deleted_at.is_(None)))).all(): items.append(TimelineItem(id=a.id, type='attachment', occurred_at=a.created_at, title=a.file_name, description=a.content_type, metadata={"storage_key": a.storage_key}))
        for s in (await self.session.scalars(select(DoctorPrioritySnapshot).where(DoctorPrioritySnapshot.organization_id==organization_id, DoctorPrioritySnapshot.hcp_id==doctor_id, DoctorPrioritySnapshot.deleted_at.is_(None)))).all(): items.append(TimelineItem(id=s.id, type='priority', occurred_at=s.created_at, title=f'Priority {s.classification}', description=s.explanation, metadata=s.factors))
        return sorted(items, key=lambda x: x.occurred_at, reverse=True)
    async def priority_history(self, organization_id: UUID, doctor_id: UUID):
        rows = list((await self.session.scalars(select(DoctorPrioritySnapshot).where(DoctorPrioritySnapshot.organization_id==organization_id, DoctorPrioritySnapshot.hcp_id==doctor_id, DoctorPrioritySnapshot.deleted_at.is_(None)).order_by(DoctorPrioritySnapshot.created_at.desc()))).all())
        return [PriorityHistoryItem(id=r.id,total_score=r.total_score,classification=r.classification,factors=r.factors,explanation=r.explanation,created_at=r.created_at) for r in rows]
    async def snapshot_priority(self, organization_id: UUID, doctor_id: UUID):
        score = await PriorityCalculationEngine().calculate(self.session, organization_id, doctor_id); explanation = '; '.join(f'{k}: {v}' for k,v in score.factors.items())
        row = DoctorPrioritySnapshot(organization_id=organization_id,hcp_id=doctor_id,total_score=score.total_score,classification=score.classification,factors=score.factors,explanation=explanation)
        self.session.add(row); await self.session.commit(); return score
    async def simulate_priority(self, organization_id: UUID, doctor_id: UUID, payload: DoctorPrioritySimulation):
        base = await PriorityCalculationEngine().calculate(self.session, organization_id, doctor_id); factors = base.factors.copy()
        mapping = {'days_since_last_visit':'days_since_last_visit','visit_frequency_30d':'visit_frequency','campaign_weight':'campaign_weight','product_priority':'product_priority','missed_visits':'missed_visits','manager_adjustment':'manager_adjustments','territory_target_gap':'territory_targets'}
        for key, factor in mapping.items():
            value = getattr(payload, key)
            if value is not None: factors[factor]=float(value)
        total = round(sum(factors.values()),2); return {"base": base, "simulated": {"total_score": total, "classification": 'high' if total>=60 else 'medium' if total>=30 else 'low', "factors": factors, "explanation": 'What-if simulation using submitted factor overrides.'}}
    async def export_csv(self, organization_id: UUID):
        doctors = await self.search(organization_id, DoctorSearchParams(limit=200)); out=io.StringIO(); writer=csv.writer(out); writer.writerow(['id','first_name','last_name','npi','email','phone','status','territory_id','specialty_id'])
        for d in doctors: writer.writerow([d.id,d.first_name,d.last_name,d.npi,d.email,d.phone,d.status,d.territory_id,d.specialty_id])
        return out.getvalue()
    async def import_csv(self, organization_id: UUID, file: UploadFile):
        text=(await file.read()).decode(); reader=csv.DictReader(io.StringIO(text)); created=0
        for row in reader:
            await self.create(organization_id, HCPCreate(territory_id=UUID(row['territory_id']), specialty_id=UUID(row['specialty_id']) if row.get('specialty_id') else None, first_name=row['first_name'], last_name=row['last_name'], npi=row.get('npi'), email=row.get('email'), phone=row.get('phone'), status=row.get('status') or 'active')) ; created+=1
        return {"created": created}
