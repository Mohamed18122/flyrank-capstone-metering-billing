from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.plan import Plan
from app.models.subscription import Subscription
from app.models.usage_event import UsageEvent
from app.services.meter import MeterService
from app.services.pricing import calculate_token_cost
from app.services.quota import QuotaExceededError


app = FastAPI(title="Usage Metering & Billing Engine")


class GenerateRequest(BaseModel):
    tenant_id: int = Field(gt=0)
    usage_type: str
    quantity: int = Field(gt=0)


@app.get("/")
def root():
    return {"message": "Usage Metering & Billing Engine is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate")
def generate(
    request: GenerateRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
    db: Session = Depends(get_db),
):
    if request.usage_type not in {"api_calls", "ai_tokens"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported usage type",
        )

    try:
        event = MeterService.record_usage(
            db=db,
            tenant_id=request.tenant_id,
            usage_type=request.usage_type,
            quantity=request.quantity,
            idempotency_key=idempotency_key,
        )

    except QuotaExceededError as exc:
        raise HTTPException(
            status_code=429,
            detail=str(exc),
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        )

    return {
        "message": "Usage recorded successfully",
        "event_id": event.id,
        "tenant_id": event.tenant_id,
        "usage_type": event.usage_type,
        "quantity": event.quantity,
        "idempotency_key": event.idempotency_key,
    }


@app.get("/usage")
def get_usage(
    tenant_id: int,
    usage_type: str,
    db: Session = Depends(get_db),
):
    if usage_type not in {"api_calls", "ai_tokens"}:
        raise HTTPException(
            status_code=400,
            detail="Unsupported usage type",
        )

    subscription = db.scalar(
        select(Subscription).where(
            Subscription.tenant_id == tenant_id
        )
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail="Tenant has no subscription",
        )

    plan = db.get(Plan, subscription.plan_id)

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Subscription plan not found",
        )

    used = db.scalar(
        select(func.coalesce(func.sum(UsageEvent.quantity), 0))
        .where(
            UsageEvent.tenant_id == tenant_id,
            UsageEvent.usage_type == usage_type,
        )
    )

    if usage_type == "api_calls":
        limit = plan.api_call_limit
        cost_cents = used * 1
    else:
        limit = plan.ai_token_limit
        cost_cents = calculate_token_cost(
            input_tokens=used,
            cached_input_tokens=0,
            output_tokens=0,
            reasoning_tokens=0,
        )

    return {
        "tenant_id": tenant_id,
        "usage_type": usage_type,
        "used": used,
        "limit": limit,
        "cost_cents": cost_cents,
    }