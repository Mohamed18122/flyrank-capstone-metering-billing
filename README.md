# Usage Metering & Billing Engine

A SaaS backend service built with Python and FastAPI for tracking API usage, enforcing quotas, calculating usage-based billing, and integrating with Stripe Test Mode.

## Features

- Tenant and subscription management
- Usage metering
- Idempotent usage recording
- Quota enforcement
- Usage-based billing calculations
- Stripe Checkout integration
- Stripe webhook handling
- PostgreSQL database
- Docker Compose support
- Automated tests

## Tech Stack

- Python 3.13
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker / Docker Compose
- Stripe
- Pytest

## Project Structure

```text
app/
├── models/
├── routers/
├── schemas/
├── services/
├── database.py
└── main.py

tests/
├── test_meter.py
├── test_pricing.py
└── test_quota.py

.env
.env.example
.gitignore
docker-compose.yml
init_db.py
requirements.txt
capstone.yaml
README.md
```

## Requirements

- Python 3.10+
- Docker Desktop
- Docker Compose
- Stripe account in Test Mode

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Mohamed18122/flyrank-capstone-metering-billing.git
cd flyrank-capstone-metering-billing
```

### 2. Create a virtual environment

```powershell
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file based on `.env.example`.

Do not commit `.env` because it contains secrets.

Example:

```env
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/metering
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 5. Start PostgreSQL

```powershell
docker compose up -d
```

Check the database container:

```powershell
docker ps
```

### 6. Initialize the database

```powershell
python init_db.py
```

## Run the API

Start the FastAPI development server:

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

## API Endpoints

### Health

- `GET /`
- `GET /health`

### Plans

- `GET /plans`

### Usage Metering

- `POST /generate`
- `GET /usage`

`POST /generate` requires an `Idempotency-Key` header.

Supported usage types:

- `api_calls`
- `ai_tokens`

Example request:

```http
POST /generate
Idempotency-Key: example-001
Content-Type: application/json
```

```json
{
  "tenant_id": 1,
  "usage_type": "api_calls",
  "quantity": 100
}
```

Example successful response:

```json
{
  "message": "Usage recorded successfully",
  "event_id": 1,
  "tenant_id": 1,
  "usage_type": "api_calls",
  "quantity": 100,
  "idempotency_key": "example-001"
}
```

### Usage

```text
GET /usage?tenant_id=1&usage_type=api_calls
```

Example response:

```json
{
  "tenant_id": 1,
  "usage_type": "api_calls",
  "used": 1100,
  "limit": 10000,
  "cost_cents": 1100
}
```

### Stripe Checkout

- `POST /checkout`
- `GET /checkout/success`
- `GET /checkout/cancel`

The checkout endpoint creates a Stripe Test Mode subscription Checkout Session.

Example:

```text
POST /checkout?tenant_id=1
```

The endpoint returns a Stripe Checkout URL.

### Stripe Webhook

- `POST /webhooks/stripe`

The webhook validates the Stripe signature and synchronizes subscription information with the local PostgreSQL database.

## Stripe Test Mode

The project uses Stripe Test Mode for subscription checkout and webhook processing.

A Checkout Session can be created through the API. The returned `checkout_url` can be opened in a browser to complete a test payment.

Only Stripe test cards should be used during development.

Stripe webhook events are used to synchronize subscription state between Stripe and the local database.

The webhook endpoint requires a valid Stripe signature.

## Quota Enforcement

Each tenant has a subscription associated with a plan.

Example plans:

| Plan | API Calls | AI Tokens |
|------|-----------|-----------|
| Free | 1,000 | 100,000 |
| Pro | 10,000 | 1,000,000 |

Usage is rejected when recording it would exceed the plan limit.

Quota violations return an HTTP `429` response through the API.

Example error:

```json
{
  "detail": "api_calls quota exceeded: used=1100, requested=8901, limit=10000"
}
```

## Idempotency

Usage events use a tenant-scoped idempotency key.

Submitting the same usage event more than once with the same tenant and idempotency key does not create a duplicate usage event.

This prevents duplicate usage from being recorded when a request is retried.

## Pricing

Token pricing is calculated using integer arithmetic in cents to avoid floating-point money errors.

Current pricing:

| Token Type | Price per 1M tokens |
|------------|---------------------|
| Fresh input | 500 cents |
| Cached input | 50 cents |
| Output | 1,500 cents |

Reasoning tokens are billed together with output tokens.

The pricing service supports:

- Input tokens
- Cached input tokens
- Output tokens
- Reasoning tokens

The pricing service validates:

- Negative input token counts
- Negative cached input token counts
- Negative output token counts
- Negative reasoning token counts
- Cached input tokens exceeding total input tokens

Example:

```python
calculate_token_cost(
    input_tokens=1_000_000,
    cached_input_tokens=0,
    output_tokens=1_000_000,
    reasoning_tokens=0,
)
```

Returns:

```text
2000
```

The returned value represents cents.

## Database

The application uses PostgreSQL through SQLAlchemy.

The database contains:

- Tenants
- Plans
- Subscriptions
- Usage events

### Database Verification

PostgreSQL can be inspected through the Docker container.

Example:

```powershell
docker exec -it task-db psql -U postgres -d metering
```

### Check Usage Events

```sql
SELECT
    id,
    tenant_id,
    usage_type,
    quantity,
    idempotency_key,
    created_at
FROM usage_events
ORDER BY id;
```

### Check Subscriptions

```sql
SELECT
    id,
    tenant_id,
    plan_id,
    stripe_customer_id,
    stripe_subscription_id,
    status
FROM subscriptions;
```

## Docker

Start the PostgreSQL database:

```powershell
docker compose up -d
```

Check running containers:

```powershell
docker ps
```

Check PostgreSQL readiness:

```powershell
docker exec -it task-db pg_isready -U postgres -d metering
```

Expected result:

```text
accepting connections
```

## Testing

Run the complete test suite with:

```powershell
python -m pytest
```

Expected result:

```text
6 passed
```

The test suite covers:

- Usage metering
- Idempotency
- Token pricing
- Pricing validation
- Quota enforcement

## Security

- Secrets are stored in `.env`.
- `.env` is excluded from Git using `.gitignore`.
- `.env.example` contains only example configuration values.
- Stripe is configured for Test Mode during development.
- Real payment credentials must never be committed to the repository.
- Stripe webhook signatures are verified before processing webhook events.

## Development Notes

This project was developed as part of the FlyRank Backend AI Engineering Capstone.

The main goal is to demonstrate reliable backend design for SaaS usage metering and billing, including:

- Idempotent usage recording
- Quota enforcement
- PostgreSQL persistence
- Integer-based monetary calculations
- Stripe Test Mode integration
- Stripe webhook handling
- Automated testing
