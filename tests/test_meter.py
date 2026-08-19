from app.database import SessionLocal
from app.services.meter import MeterService


def test_duplicate_idempotency_key_does_not_create_duplicate():
    db = SessionLocal()

    try:
        first = MeterService.record_usage(
            db=db,
            tenant_id=1,
            usage_type="ai_tokens",
            quantity=100,
            idempotency_key="pytest-idempotency-001",
        )

        second = MeterService.record_usage(
            db=db,
            tenant_id=1,
            usage_type="ai_tokens",
            quantity=100,
            idempotency_key="pytest-idempotency-001",
        )

        assert first.id == second.id
        assert first.quantity == second.quantity

    finally:
        db.close()