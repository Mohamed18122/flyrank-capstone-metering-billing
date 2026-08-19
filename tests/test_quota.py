import pytest

from app.database import SessionLocal
from app.services.meter import MeterService
from app.services.quota import QuotaExceededError


def test_quota_rejects_usage_over_limit():
    db = SessionLocal()

    try:
        with pytest.raises(QuotaExceededError):
            MeterService.record_usage(
                db=db,
                tenant_id=1,
                usage_type="api_calls",
                quantity=1,
                idempotency_key="pytest-quota-over-limit-001",
            )

    finally:
        db.close()