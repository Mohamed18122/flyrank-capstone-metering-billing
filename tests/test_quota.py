import pytest
from sqlalchemy import func

from app.database import SessionLocal
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.usage_event import UsageEvent
from app.services.quota import QuotaExceededError, QuotaService


def test_quota_rejects_usage_over_limit():
    db = SessionLocal()

    try:
        subscription = db.query(Subscription).filter(
            Subscription.tenant_id == 1
        ).first()

        plan = db.get(Plan, subscription.plan_id)

        current_usage = db.query(
            func.coalesce(func.sum(UsageEvent.quantity), 0)
        ).filter(
            UsageEvent.tenant_id == 1,
            UsageEvent.usage_type == "api_calls",
        ).scalar()

        requested_quantity = plan.api_call_limit - current_usage + 1

        with pytest.raises(QuotaExceededError):
            QuotaService.check_quota(
                db=db,
                tenant_id=1,
                usage_type="api_calls",
                requested_quantity=requested_quantity,
            )

    finally:
        db.close()