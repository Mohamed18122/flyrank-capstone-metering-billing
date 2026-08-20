import os

import stripe
from sqlalchemy.orm import Session

from app.models.plan import Plan
from app.models.subscription import Subscription


stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_checkout_session(
    db: Session,
    tenant_id: int,
) -> str:
    subscription = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant_id)
        .first()
    )

    if not subscription:
        raise ValueError("Tenant has no subscription")

    pro_plan = (
        db.query(Plan)
        .filter(Plan.name == "Pro")
        .first()
    )

    if not pro_plan:
        raise ValueError("Pro plan not found")

    if not stripe.api_key:
        raise ValueError("STRIPE_SECRET_KEY is not set")

    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": "Pro Plan",
                    },
                    "unit_amount": pro_plan.monthly_price_cents,
                    "recurring": {
                        "interval": "month",
                    },
                },
                "quantity": 1,
            }
        ],
        metadata={
            "tenant_id": str(tenant_id),
            "plan_id": str(pro_plan.id),
        },
        success_url="http://127.0.0.1:8000/checkout/success",
        cancel_url="http://127.0.0.1:8000/checkout/cancel",
    )

    return session.url