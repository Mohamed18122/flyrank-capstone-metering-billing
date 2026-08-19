from app.database import Base, engine, SessionLocal
from app.models import Plan, Tenant, Subscription, UsageEvent


Base.metadata.create_all(bind=engine)


with SessionLocal() as db:
    plans = [
        {
            "name": "Free",
            "api_call_limit": 1000,
            "ai_token_limit": 100000,
            "monthly_price_cents": 0,
        },
        {
            "name": "Pro",
            "api_call_limit": 10000,
            "ai_token_limit": 1000000,
            "monthly_price_cents": 2900,
        },
    ]

    for plan_data in plans:
        existing_plan = (
            db.query(Plan)
            .filter(Plan.name == plan_data["name"])
            .first()
        )

        if not existing_plan:
            db.add(Plan(**plan_data))

    db.commit()

    free_plan = (
        db.query(Plan)
        .filter(Plan.name == "Free")
        .first()
    )

    tenant = (
        db.query(Tenant)
        .filter(Tenant.name == "Demo Tenant")
        .first()
    )

    if not tenant:
        tenant = Tenant(name="Demo Tenant")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    subscription = (
        db.query(Subscription)
        .filter(Subscription.tenant_id == tenant.id)
        .first()
    )

    if not subscription:
        subscription = Subscription(
            tenant_id=tenant.id,
            plan_id=free_plan.id,
            status="active",
        )
        db.add(subscription)
        db.commit()


print("Database tables, plans, and demo tenant are ready.")