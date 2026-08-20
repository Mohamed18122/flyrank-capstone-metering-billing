\# Evidence



\## Project



Usage Metering \& Billing Engine



GitHub:

https://github.com/Mohamed18122/flyrank-capstone-metering-billing



\## API Health



Endpoint:



GET /health



Result:



{

&#x20; "status": "ok"

}



The FastAPI application is running successfully.



\## Automated Tests



Command:



python -m pytest



Result:



6 passed in 0.62s



The test suite covers:



\- Usage metering

\- Idempotency

\- Token pricing

\- Pricing validation

\- Quota enforcement



\## PostgreSQL / Docker



Docker containers were verified using:



docker ps



PostgreSQL 17 containers were running successfully.



PostgreSQL readiness was also verified using:



docker exec -it task-db pg\_isready -U postgres -d metering



Result:



accepting connections



\## Usage Metering



Usage events were verified directly in PostgreSQL.



Command:



docker exec -it task-db psql -U postgres -d metering -c "SELECT id, tenant\_id, usage\_type, quantity, idempotency\_key FROM usage\_events ORDER BY id;"



Verified usage records include:



\- api\_calls usage

\- ai\_tokens usage

\- tenant\_id 1

\- persisted idempotency keys



This demonstrates that usage events are persisted in PostgreSQL.



\## Idempotency



Usage events use a tenant-scoped idempotency key.



Submitting the same usage event more than once with the same tenant and idempotency key does not create a duplicate usage event.



The automated test:



test\_duplicate\_idempotency\_key\_does\_not\_create\_duplicate



passes successfully.



Temporary test records were cleaned from the database after verification.



\## Quota Enforcement



Quota enforcement was tested using:



test\_quota\_rejects\_usage\_over\_limit



The test fills the remaining quota and then attempts to record additional usage.



The additional usage is rejected with QuotaExceededError.



The test passes successfully.



The API converts quota violations into HTTP 429 responses.



Example:



{

&#x20; "detail": "api\_calls quota exceeded"

}



This verifies that usage cannot exceed the plan limit.



\## Pricing



The pricing service uses integer arithmetic in cents.



The pricing tests verify:



\- Input token pricing

\- Cached input token pricing

\- Output token pricing

\- Reasoning token pricing

\- Negative token validation

\- Cached input validation



All pricing tests pass.



Money calculations avoid floating-point precision errors.



\## API Endpoints



The application provides:



GET /



GET /health



GET /plans



POST /generate



GET /usage



POST /checkout



GET /checkout/success



GET /checkout/cancel



POST /webhooks/stripe



\## Generate Usage



POST /generate requires an Idempotency-Key header.



Supported usage types:



\- api\_calls

\- ai\_tokens



Example request:



POST /generate



Idempotency-Key: example-001



{

&#x20; "tenant\_id": 1,

&#x20; "usage\_type": "api\_calls",

&#x20; "quantity": 100

}



The endpoint validates the usage type, tenant subscription, quota and idempotency key before recording the usage event.



\## Usage



The application provides:



GET /usage?tenant\_id=1\&usage\_type=api\_calls



The endpoint returns:



\- Tenant ID

\- Usage type

\- Current usage

\- Plan limit

\- Calculated cost in cents



\## Plans



The application provides:



GET /plans



Example plans:



| Plan | API Calls | AI Tokens |

|------|-----------|-----------|

| Free | 1,000 | 100,000 |

| Pro | 10,000 | 1,000,000 |



\## Stripe Checkout



The application provides:



POST /checkout



Example:



POST /checkout?tenant\_id=1



The endpoint creates a Stripe Checkout Session in Stripe Test Mode.



The response contains a checkout URL.



The Checkout Session is configured as a subscription checkout for the Pro plan.



\## Stripe Success Page



Endpoint:



GET /checkout/success



Verified response:



{

&#x20; "message": "Payment successful",

&#x20; "status": "success"

}



\## Stripe Cancel Page



Endpoint:



GET /checkout/cancel



The endpoint provides a cancellation response when checkout is cancelled.



\## Stripe Webhook Security



The application provides:



POST /webhooks/stripe



A request without a Stripe signature was tested.



Result:



{

&#x20; "detail": "Missing Stripe signature"

}



A request with a fake Stripe signature was also tested.



Result:



{

&#x20; "detail": "Invalid webhook signature"

}



This demonstrates that the webhook rejects unsigned and invalidly signed requests.



\## Stripe Webhook Processing



The webhook handles:



checkout.session.completed



When a valid Stripe event is received, the application synchronizes subscription information with the local PostgreSQL database.



The synchronized information includes:



\- Stripe customer ID

\- Stripe subscription ID

\- Tenant ID

\- Plan ID

\- Subscription status



\## Database Verification



PostgreSQL can be inspected using:



docker exec -it task-db psql -U postgres -d metering



\### Usage Events



SELECT

&#x20;   id,

&#x20;   tenant\_id,

&#x20;   usage\_type,

&#x20;   quantity,

&#x20;   idempotency\_key,

&#x20;   created\_at

FROM usage\_events

ORDER BY id;



\### Subscriptions



SELECT

&#x20;   id,

&#x20;   tenant\_id,

&#x20;   plan\_id,

&#x20;   stripe\_customer\_id,

&#x20;   stripe\_subscription\_id,

&#x20;   status

FROM subscriptions;



These queries verify that usage and subscription information are persisted in PostgreSQL.



\## Security



Secrets are stored in .env.



The following environment variables are used:



DATABASE\_URL



STRIPE\_SECRET\_KEY



STRIPE\_WEBHOOK\_SECRET



The .env file is excluded from Git.



.env.example contains only example configuration values.



Stripe is configured for Test Mode during development.



Real payment credentials must never be committed to the repository.



Stripe webhook signatures are verified before processing webhook events.



\## GitHub



Repository:



https://github.com/Mohamed18122/flyrank-capstone-metering-billing



The project was successfully pushed to GitHub.



Final Git status:



On branch main



Your branch is up to date with 'origin/main'.



nothing to commit, working tree clean



\## Final Verification



Automated tests:



6 passed



API health:



{

&#x20; "status": "ok"

}



Docker/PostgreSQL:



PostgreSQL container running successfully.



Git:



working tree clean



\## Capstone Requirements Demonstrated



The project demonstrates:



\- FastAPI backend development

\- PostgreSQL database persistence

\- Docker Compose support

\- Tenant and subscription management

\- Usage metering

\- Idempotent usage recording

\- Quota enforcement

\- Usage-based billing calculations

\- Integer-based monetary calculations

\- Stripe Test Mode Checkout

\- Stripe webhook handling

\- Stripe webhook signature verification

\- Subscription synchronization

\- Automated testing

\- GitHub repository delivery



\## Conclusion



The Usage Metering \& Billing Engine capstone has been implemented and verified locally.



The system provides a reliable SaaS backend for usage tracking, quota enforcement, idempotency, billing calculations, PostgreSQL persistence, and Stripe Test Mode integration.

