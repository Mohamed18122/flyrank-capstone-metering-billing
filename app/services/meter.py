from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usage_event import UsageEvent
from app.services.quota import QuotaService


class MeterService:

    @staticmethod
    def record_usage(
        db: Session,
        tenant_id: int,
        usage_type: str,
        quantity: int,
        idempotency_key: str,
    ) -> UsageEvent:

        existing_event = db.scalar(
            select(UsageEvent).where(
                UsageEvent.tenant_id == tenant_id,
                UsageEvent.idempotency_key == idempotency_key,
            )
        )

        if existing_event:
            return existing_event

        QuotaService.check_quota(
            db=db,
            tenant_id=tenant_id,
            usage_type=usage_type,
            requested_quantity=quantity,
        )

        event = UsageEvent(
            tenant_id=tenant_id,
            usage_type=usage_type,
            quantity=quantity,
            idempotency_key=idempotency_key,
        )

        db.add(event)
        db.commit()
        db.refresh(event)

        return event