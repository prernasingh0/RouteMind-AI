from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.models import Campaign, HCP, Product, ProductPriorityRule, Territory, Visit
from app.schemas.business import PriorityBreakdown

class PriorityRuleStrategy(ABC):
    name: str
    @abstractmethod
    async def score(self, session: AsyncSession, doctor: HCP) -> float: ...

class DaysSinceLastVisitRule(PriorityRuleStrategy):
    name = "days_since_last_visit"
    async def score(self, session, doctor):
        last = await session.scalar(select(func.max(Visit.completed_at)).where(Visit.organization_id==doctor.organization_id, Visit.hcp_id==doctor.id, Visit.deleted_at.is_(None)))
        if not last: return 20.0
        if last.tzinfo is None: last = last.replace(tzinfo=timezone.utc)
        return min(max((datetime.now(timezone.utc)-last).days / 3, 0), 20)

class VisitFrequencyRule(PriorityRuleStrategy):
    name = "visit_frequency"
    async def score(self, session, doctor):
        since = datetime.now(timezone.utc) - timedelta(days=30)
        count = await session.scalar(select(func.count(Visit.id)).where(Visit.organization_id==doctor.organization_id, Visit.hcp_id==doctor.id, Visit.completed_at >= since, Visit.deleted_at.is_(None))) or 0
        return max(15 - float(count) * 4, 0)

class CampaignWeightRule(PriorityRuleStrategy):
    name = "campaign_weight"
    async def score(self, session, doctor):
        active = await session.scalar(select(func.coalesce(func.sum(Campaign.weight), 0.0)).where(Campaign.organization_id==doctor.organization_id, Campaign.is_active.is_(True), Campaign.deleted_at.is_(None))) or 0
        return min(float(active) * 5, 15)

class ProductPriorityRuleStrategy(PriorityRuleStrategy):
    name = "product_priority"
    async def score(self, session, doctor):
        product_weight = await session.scalar(select(func.coalesce(func.sum(Product.priority_weight), 0.0)).where(Product.organization_id==doctor.organization_id, Product.is_active.is_(True), Product.deleted_at.is_(None))) or 0
        rule_weight = await session.scalar(select(func.coalesce(func.sum(ProductPriorityRule.weight), 0.0)).where(ProductPriorityRule.organization_id==doctor.organization_id, ProductPriorityRule.deleted_at.is_(None), (ProductPriorityRule.territory_id == doctor.territory_id) | (ProductPriorityRule.territory_id.is_(None)))) or 0
        return min(float(product_weight) + float(rule_weight) * 5, 15)

class MissedVisitsRule(PriorityRuleStrategy):
    name = "missed_visits"
    async def score(self, session, doctor):
        count = await session.scalar(select(func.count(Visit.id)).where(Visit.organization_id==doctor.organization_id, Visit.hcp_id==doctor.id, Visit.status.in_(["missed", "cancelled"]), Visit.deleted_at.is_(None))) or 0
        return min(float(count) * 5, 15)

class ManagerAdjustmentRule(PriorityRuleStrategy):
    name = "manager_adjustments"
    async def score(self, session, doctor): return max(min(float(doctor.manager_adjustment), 15), -15)

class TerritoryTargetsRule(PriorityRuleStrategy):
    name = "territory_targets"
    async def score(self, session, doctor):
        territory = await session.get(Territory, doctor.territory_id)
        if not territory: return 0
        completed = await session.scalar(select(func.count(Visit.id)).where(Visit.organization_id==doctor.organization_id, Visit.hcp_id==doctor.id, Visit.completed_at.is_not(None), Visit.deleted_at.is_(None))) or 0
        return 10 if completed < max(territory.target_visits_per_month / 10, 1) else 0

class PriorityCalculationEngine:
    def __init__(self, strategies: list[PriorityRuleStrategy] | None = None) -> None:
        self.strategies = strategies or [DaysSinceLastVisitRule(), VisitFrequencyRule(), CampaignWeightRule(), ProductPriorityRuleStrategy(), MissedVisitsRule(), ManagerAdjustmentRule(), TerritoryTargetsRule()]
    async def calculate(self, session: AsyncSession, organization_id: UUID, hcp_id: UUID) -> PriorityBreakdown:
        doctor = await session.scalar(select(HCP).where(HCP.id==hcp_id, HCP.organization_id==organization_id, HCP.deleted_at.is_(None)))
        if not doctor:
            from fastapi import HTTPException, status
            raise HTTPException(status.HTTP_404_NOT_FOUND, "HCP not found")
        factors = {s.name: round(await s.score(session, doctor), 2) for s in self.strategies}
        total = round(sum(factors.values()) + max(doctor.engagement_score, 0) + max(doctor.prescription_trend, 0), 2)
        classification = "high" if total >= 60 else "medium" if total >= 30 else "low"
        return PriorityBreakdown(hcp_id=hcp_id, total_score=total, classification=classification, factors=factors)
