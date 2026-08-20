\# Usage Metering \& Billing Engine



A SaaS backend service built with Python and FastAPI for tracking API usage, enforcing quotas, calculating usage-based billing, and integrating with Stripe Test Mode.



\## Features



\* Tenant and subscription management

\* Usage metering

\* Idempotent usage recording

\* Quota enforcement

\* Usage-based billing calculations

\* Stripe Checkout integration

\* Stripe webhook handling

\* PostgreSQL database

\* Docker Compose support

\* Automated tests



\## Tech Stack



\* Python 3.13

\* FastAPI

\* SQLAlchemy

\* PostgreSQL

\* Docker / Docker Compose

\* Stripe

\* Pytest



\## Project Structure



```text

app/

├── models/

├── routers/

├── schemas/

├── services/

├── database.py

└── main.py



tests/

.env

.env.example

docker-compose.yml

init\_db.py

requirements.txt

capstone.yaml

```



\## Requirements



\* Python 3.10+

\* Docker Desktop

\* Docker Compose

\* Stripe account in Test Mode



\## Setup



\### 1. Clone the repository



```bash

git clone https://github.com/Mohamed18122/flyrank-capstone-metering-billing.git

cd flyrank-capstone-metering-billing

```



\### 2. Create a virtual environment



```powershell

python -m venv venv

```



Activate it on Windows:



```powershell

.\\venv\\Scripts\\Activate.ps1

```



\### 3. Install dependencies



```powershell

pip install -r requirements.txt

```



\### 4. Configure environment variables



Create a local `.env` file based on `.env.example`.



Do not commit `.env` because it contains secrets.



Example:



```env

DATABASE\_URL=postgresql+psycopg://postgres:postgres@localhost:5432/metering

STRIPE\_SECRET\_KEY=sk\_test\_...

STRIPE\_WEBHOOK\_SECRET=whsec\_...

```



\### 5. Start PostgreSQL



```powershell

docker compose up -d

```



Check the database container:



```powershell

docker ps

```



\### 6. Initialize the database



```powershell

python init\_db.py

```



\## Run the API



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



\## Stripe Test Mode



The project uses Stripe Test Mode for subscription checkout and webhook processing.



A Checkout Session can be created through the API. The returned `checkout\_url` can be opened in a browser to complete a test payment.



Only Stripe test cards should be used during development.



Stripe webhook events are used to synchronize subscription state between Stripe and the local database.



\## Database Verification



PostgreSQL can be inspected through the Docker container.



Example:



```powershell

docker exec -it task-db psql -U postgres -d metering

```



Example subscription query:



```sql

SELECT

&#x20;   id,

&#x20;   tenant\_id,

&#x20;   plan\_id,

&#x20;   stripe\_customer\_id,

&#x20;   stripe\_subscription\_id,

&#x20;   status

FROM subscriptions;

```



\## Testing



Run the test suite with:



```powershell

pytest

```



\## Security



\* Secrets are stored in `.env`.

\* `.env` is excluded from Git using `.gitignore`.

\* `.env.example` contains only example configuration values.

\* Stripe is configured for Test Mode during development.

\* Real payment credentials must never be committed to the repository.



\## Development Notes



This project was developed as part of the FlyRank Backend AI Engineering Capstone.



The main goal is to demonstrate reliable backend design for SaaS usage metering and billing, including idempotency, quota enforcement, monetary calculations, and Stripe integration.



