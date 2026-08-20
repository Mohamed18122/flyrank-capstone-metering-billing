\# Build Log



\## Project



Usage Metering \& Billing Engine



FlyRank Backend AI Engineering Capstone



GitHub:

https://github.com/Mohamed18122/flyrank-capstone-metering-billing



\---



\## Phase 1 - Project Setup



Created the capstone repository:



flyrank-capstone-metering-billing



Created the Python virtual environment:



python -m venv venv



Activated the virtual environment on Windows:



.\\venv\\Scripts\\Activate.ps1



Python version:



Python 3.13.14



Installed the project dependencies from requirements.txt.



\---



\## Phase 2 - FastAPI Application



Created the FastAPI application structure:



app/

\- models/

\- routers/

\- schemas/

\- services/

\- database.py

\- main.py



Implemented the main FastAPI application.



Added:



GET /



GET /health



The health endpoint returns:



{

&#x20; "status": "ok"

}



The API was successfully started with:



uvicorn app.main:app --reload



Base URL:



http://127.0.0.1:8000



Swagger documentation:



http://127.0.0.1:8000/docs



\---



\## Phase 3 - Database



PostgreSQL was selected as the application database.



Docker Compose was configured to run PostgreSQL 17.



The database uses SQLAlchemy for database access.



The database contains the following main entities:



\- Tenants

\- Plans

\- Subscriptions

\- Usage Events



PostgreSQL readiness was verified using:



docker exec -it task-db pg\_isready -U postgres -d metering



The database successfully reported:



accepting connections



\---



\## Phase 4 - Plans and Subscriptions



Implemented plan and subscription models.



Plans contain:



\- Plan name

\- API call limit

\- AI token limit

\- Monthly price in cents



Example plans:



Free:

\- 1,000 API calls

\- 100,000 AI tokens



Pro:

\- 10,000 API calls

\- 1,000,000 AI tokens



Subscriptions associate tenants with plans.



\---



\## Phase 5 - Usage Metering



Implemented the MeterService for recording usage.



Supported usage types:



\- api\_calls

\- ai\_tokens



Usage events store:



\- Tenant ID

\- Usage type

\- Quantity

\- Idempotency key

\- Creation timestamp



Implemented:



POST /generate



The endpoint requires an Idempotency-Key header.



Example request:



POST /generate



Idempotency-Key: example-001



{

&#x20; "tenant\_id": 1,

&#x20; "usage\_type": "api\_calls",

&#x20; "quantity": 100

}



Usage events are persisted in PostgreSQL.



\---



\## Phase 6 - Idempotency



Implemented tenant-scoped idempotency for usage events.



The same tenant cannot create duplicate usage for the same idempotency key.



This protects the metering system from duplicate requests and retries.



Automated test implemented:



test\_duplicate\_idempotency\_key\_does\_not\_create\_duplicate



The test passes successfully.



Temporary test records were removed from the database after verification.



\---



\## Phase 7 - Quota Enforcement



Implemented quota enforcement through the subscription plan.



Before recording usage, the service checks the tenant's current usage against the plan limit.



If the requested usage would exceed the plan limit, the request is rejected.



Implemented:



QuotaExceededError



The API converts quota violations to HTTP 429.



Automated test implemented:



test\_quota\_rejects\_usage\_over\_limit



The test passes successfully.



\---



\## Phase 8 - Usage Endpoint



Implemented:



GET /usage



Example:



GET /usage?tenant\_id=1\&usage\_type=api\_calls



The endpoint calculates:



\- Current usage

\- Plan limit

\- Usage cost



The endpoint supports:



\- api\_calls

\- ai\_tokens



\---



\## Phase 9 - Pricing



Implemented token pricing using integer arithmetic in cents.



The pricing service supports:



\- Input tokens

\- Cached input tokens

\- Output tokens

\- Reasoning tokens



The pricing service validates:



\- Negative input tokens

\- Negative cached input tokens

\- Negative output tokens

\- Negative reasoning tokens

\- Cached input tokens greater than total input tokens



Integer arithmetic is used to avoid floating-point money calculation errors.



Automated pricing tests were implemented.



All pricing tests pass.



\---



\## Phase 10 - Stripe Checkout



Added Stripe Test Mode integration.



Implemented:



POST /checkout



The endpoint creates a Stripe Checkout Session for the Pro subscription.



The checkout session includes:



\- Subscription mode

\- Pro plan pricing

\- Tenant metadata

\- Plan metadata

\- Success URL

\- Cancel URL



Stripe secret credentials are loaded from environment variables.



The endpoint returns the Stripe checkout URL.



\---



\## Phase 11 - Stripe Success and Cancel Pages



Implemented:



GET /checkout/success



Successful checkout response:



{

&#x20; "message": "Payment successful",

&#x20; "status": "success"

}



Implemented:



GET /checkout/cancel



This endpoint handles cancelled checkout sessions.



\---



\## Phase 12 - Stripe Webhook



Implemented:



POST /webhooks/stripe



The webhook receives the raw Stripe request body and validates the Stripe signature.



The endpoint rejects requests without a Stripe signature.



Verified response:



{

&#x20; "detail": "Missing Stripe signature"

}



Invalid signatures are also rejected.



Verified response:



{

&#x20; "detail": "Invalid webhook signature"

}



This protects webhook processing from unauthorized requests.



\---



\## Phase 13 - Stripe Subscription Synchronization



Implemented handling for:



checkout.session.completed



The webhook reads the tenant and plan information from Stripe Checkout metadata.



The application synchronizes:



\- Stripe customer ID

\- Stripe subscription ID

\- Tenant ID

\- Plan ID

\- Subscription status



The local PostgreSQL subscription record is updated after successful webhook processing.



\---



\## Phase 14 - Environment Configuration



Configured environment variables through .env.



Variables include:



DATABASE\_URL



STRIPE\_SECRET\_KEY



STRIPE\_WEBHOOK\_SECRET



The .env file is excluded from Git.



.env.example contains example configuration only.



No real payment credentials are committed to the repository.



\---



\## Phase 15 - Testing



Implemented automated tests for the core backend functionality.



Test files:



tests/

\- test\_meter.py

\- test\_pricing.py

\- test\_quota.py



Executed:



python -m pytest



Final result:



6 passed



The test suite covers:



\- Usage metering

\- Idempotency

\- Pricing calculations

\- Pricing validation

\- Quota enforcement



One SQLAlchemy deprecation warning appeared during earlier runs because datetime.utcnow() is deprecated in a future Python version.



The warning does not cause test failures.



\---



\## Phase 16 - Database Verification



Verified usage events directly in PostgreSQL.



Example records included:



\- api\_calls usage

\- ai\_tokens usage

\- tenant ID

\- quantity

\- idempotency key



Temporary quota and idempotency test records were cleaned after testing.



The remaining database records were verified successfully.



\---



\## Phase 17 - API Verification



Verified the API health endpoint:



GET /health



Result:



{

&#x20; "status": "ok"

}



Verified the Stripe success endpoint:



GET /checkout/success



Result:



{

&#x20; "message": "Payment successful",

&#x20; "status": "success"

}



Verified Stripe webhook security with:



\- Missing signature

\- Invalid signature



Both cases were rejected correctly.



\---



\## Phase 18 - Docker Verification



Verified running containers using:



docker ps



PostgreSQL containers were running successfully.



Verified PostgreSQL connectivity using:



docker exec -it task-db pg\_isready -U postgres -d metering



Result:



accepting connections



\---



\## Phase 19 - Documentation



Created and updated:



README.md



EVIDENCE.md



BUILDLOG.md



capstone.yaml



.env.example



The README documents:



\- Project purpose

\- Features

\- Technology stack

\- Setup instructions

\- API endpoints

\- Database usage

\- Stripe integration

\- Testing

\- Security



The evidence file documents the verification results.



This build log documents the implementation process.



\---



\## Phase 20 - Git



Committed project changes to Git.



Important commits include:



Fix quota test and app package



and the final README documentation update.



The project was pushed successfully to GitHub.



Repository:



https://github.com/Mohamed18122/flyrank-capstone-metering-billing



Final Git status:



On branch main



Your branch is up to date with 'origin/main'.



nothing to commit, working tree clean



\---



\## Final Verification



API:



GET /health



Result:



{

&#x20; "status": "ok"

}



Tests:



python -m pytest



Result:



6 passed



Docker:



PostgreSQL running successfully.



Git:



working tree clean



\---



\## Final Capstone Features



The completed application provides:



\- FastAPI backend

\- PostgreSQL persistence

\- Docker Compose support

\- Tenant management

\- Subscription management

\- Plan management

\- Usage metering

\- Idempotent usage recording

\- Quota enforcement

\- Usage reporting

\- Integer-based billing calculations

\- Stripe Test Mode Checkout

\- Stripe success and cancel pages

\- Stripe webhook handling

\- Stripe signature verification

\- Subscription synchronization

\- Automated tests

\- Security through environment variables

\- GitHub repository delivery



\---



\## Conclusion



The Usage Metering \& Billing Engine was implemented as the FlyRank Backend AI Engineering Capstone.



The system demonstrates reliable backend engineering practices for a SaaS billing platform, including usage metering, idempotency, quota enforcement, monetary calculations, PostgreSQL persistence, Docker support, Stripe Test Mode integration, webhook verification, and automated testing.



The final implementation was tested locally and pushed successfully to GitHub.



