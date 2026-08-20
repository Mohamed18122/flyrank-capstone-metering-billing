import os

from dotenv import load_dotenv

load_dotenv()

import stripe
from fastapi import Depends, FastAPI, Header, HTTPException, Request
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
from app.services.stripe_service import create_checkout_session


app = FastAPI(title="Usage Metering & Billing Engine")


stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


class GenerateRequest(BaseModel):
    tenant_id: int = Field(gt=0)
    usage_type: str
    quantity: int = Field(gt=0)


@app.get("/")
def root():
    return {
        "message": "Usage Metering & Billing Engine is running"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/plans")
def get_plans(
    db: Session = Depends(get_db),
):
    plans = db.scalars(
        select(Plan).order_by(Plan.id)
    ).all()

    return [
        {
            "id": plan.id,
            "name": plan.name,
            "api_call_limit": plan.api_call_limit,
            "ai_token_limit": plan.ai_token_limit,
            "monthly_price_cents": plan.monthly_price_cents,
        }
        for plan in plans
    ]


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


@app.post("/checkout")
def create_checkout(
    tenant_id: int,
    db: Session = Depends(get_db),
):
    try:
        checkout_url = create_checkout_session(
            db=db,
            tenant_id=tenant_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except stripe.error.StripeError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Stripe error: {str(exc)}",
        )

    return {
        "checkout_url": checkout_url,
    }


@app.get("/checkout/success")
def checkout_success():
    return {
        "message": "Payment successful",
        "status": "success",
    }


@app.get("/checkout/cancel")
def checkout_cancel():
    return {
        "message": "Checkout canceled",
        "status": "cancelled",
    }


@app.post("/webhooks/stripe")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    payload = await request.body()
    signature = request.headers.get("stripe-signature")

    if not signature:
        raise HTTPException(
            status_code=400,
            detail="Missing Stripe signature",
        )

    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(
            status_code=500,
            detail="STRIPE_WEBHOOK_SECRET is not configured",
        )

    try:
        event = stripe.Webhook.construct_event(
            payload,
            signature,
            STRIPE_WEBHOOK_SECRET,
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook payload",
        )

    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=400,
            detail="Invalid webhook signature",
        )

    event_type = event["type"]

    print(f"Stripe webhook received: {event_type}")

    if event_type == "checkout.session.completed":
        session = event["data"]["object"]

        metadata = session.metadata

        tenant_id = metadata["tenant_id"]
        plan_id = metadata["plan_id"]

        customer_id = session.customer
        stripe_subscription_id = session.subscription

        print(
            "Checkout completed:",
            f"tenant_id={tenant_id}",
            f"plan_id={plan_id}",
            f"customer={customer_id}",
            f"subscription={stripe_subscription_id}",
        )

        subscription = db.scalar(
            select(Subscription).where(
                Subscription.tenant_id == int(tenant_id)
            )
        )

        if subscription:
            subscription.stripe_customer_id = customer_id
            subscription.stripe_subscription_id = (
                stripe_subscription_id
            )
            subscription.plan_id = int(plan_id)
            subscription.status = "active"

            db.commit()

            print(
                f"Subscription updated for tenant {tenant_id}"
            )

        else:
            print(
                f"No local subscription found for tenant {tenant_id}"
            )

    return {
        "received": True,
        "event_type": event_type,
    }