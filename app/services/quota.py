from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.usage_event import UsageEvent


class QuotaExceededError(Exception):
    pass


class QuotaService:

    @staticmethod
    def check_quota(
        db: Session,
        tenant_id: int,
        usage_type: str,
        requested_quantity: int,
    ) -> None:

        subscription = db.scalar(
            select(Subscription)
            .where(Subscription.tenant_id == tenant_id)
        )

        if not subscription:
            raise ValueError("Tenant has no subscription")

        plan = db.get(Plan, subscription.plan_id)

        if not plan:
            raise ValueError("Subscription plan not found")

        current_usage = db.scalar(
            select(func.coalesce(func.sum(UsageEvent.quantity), 0))
            .where(
                UsageEvent.tenant_id == tenant_id,
                UsageEvent.usage_type == usage_type,
            )
        )

        if usage_type == "api_calls":
            limit = plan.api_call_limit
        elif usage_type == "ai_tokens":
            limit = plan.ai_token_limit
        else:
            raise ValueError("Unsupported usage type")

        if current_usage + requested_quantity > limit:
            raise QuotaExceededError(
                f"{usage_type} quota exceeded: "
                f"used={current_usage}, "
                f"requested={requested_quantity}, "
                f"limit={limit}"
            )