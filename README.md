# Insurance Management System

A backend API for an insurance agent to manage their book of business: onboard customers, issue policies, and handle the policy lifecycle (update/cancel).

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy 2.0** — ORM, with **SQLite** as the database (file-based, zero external setup)
- **Pydantic v2** — request/response validation
- **pytest** + **httpx** — testing

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the API
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`. A SQLite file (`insurance.db`) is created automatically on first run — no migrations or external DB needed.

### Running tests

```bash
pytest
```

Tests run against an isolated in-memory SQLite database (see `tests/conftest.py`) and never touch `insurance.db`.

## Architecture

The code is organized in layers, each with a single responsibility, so business rules never leak into HTTP handling and SQL never leaks into business rules:

```
app/
  core/          config, DB session/engine setup, custom domain exceptions
  models/        SQLAlchemy ORM table definitions (Customer, Policy)
  schemas/       Pydantic request/response DTOs (Create/Update/Read)
  repositories/  raw persistence operations (SELECT/INSERT/UPDATE) — no business logic
  services/      business rules: existence checks, uniqueness checks, state-transition rules
  api/routers/   HTTP layer: routes, status codes, request/response wiring
  main.py        app assembly + exception-to-HTTP-status translation
```

Flow for a request: **router** (parses HTTP, picks status codes) → **service** (enforces business rules, raises domain exceptions) → **repository** (issues the actual query) → **model** (table schema). Domain exceptions (`NotFoundError`, `ConflictError`, `BusinessRuleError`) are translated to HTTP responses (404/409/422) by handlers registered in `main.py`, so services stay framework-agnostic.

### Data model

**Customer** (the policyholder) — `id`, `full_name`, `email` (unique), `phone`, `national_id` (unique, optional), `address`, timestamps.

**Policy** — `id`, `policy_number` (unique, auto-generated), `customer_id` (FK → Customer), `policy_type` (CAR/HEALTH/LIFE/HOME), `status` (ACTIVE/CANCELLED/EXPIRED), `premium_amount`, `coverage_amount`, `start_date`/`end_date`, `cancelled_at`/`cancellation_reason`, timestamps.

It's a one-to-many relationship stored the normalized way: only `policies.customer_id` exists as a foreign key — there's no `policies` array on `Customer`. "All policies for a customer" is a query (`WHERE customer_id = :id`), not stored data. Indexes are added on `customer_id`, `policy_type`, and `status` since those are exactly the columns the filtering endpoint queries on.

**Why SQLite over Postgres/NoSQL:** the domain is inherently relational (strict FK integrity, uniqueness constraints, ACID transactions on issuance/cancellation) — a document store would mean denormalizing or manually re-implementing referential integrity for no benefit here. SQLite was chosen over a server-based RDBMS purely so the project runs with zero external infrastructure. Because everything goes through the SQLAlchemy ORM, moving to Postgres later is a one-line change to `database_url` — no application code changes. The known tradeoff: SQLite serializes writes, so it isn't meant to survive concurrent multi-agent production load — that's the first thing to swap out.

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/customers` | Onboard a new customer |
| GET | `/customers` | List customers (paginated) |
| GET | `/customers/{id}` | Get a customer |
| PATCH | `/customers/{id}` | Update customer contact details |
| POST | `/customers/{id}/policies` | Issue a new policy to that customer |
| GET | `/customers/{id}/policies` | List all policies for that customer |
| GET | `/policies` | List/filter policies by `customer_id`, `policy_type`, `status` |
| GET | `/policies/{id}` | Get a policy |
| PATCH | `/policies/{id}` | Update mutable policy details (premium, coverage, dates) |
| POST | `/policies/{id}/cancel` | Cancel/terminate a policy |

## Business Rules / Data Integrity

- A policy can only be issued to an existing customer (404 otherwise).
- `email` and `national_id` must be unique per customer (409 on conflict).
- `end_date` must be after `start_date`, and `premium_amount`/`coverage_amount` must be positive — enforced both at the Pydantic validation layer and as DB-level `CHECK` constraints.
- A policy cannot be updated or cancelled once it is already `CANCELLED` (409).
- Foreign key constraints are enforced at the database level (`PRAGMA foreign_keys=ON`), not just in application code.

## Assumptions

- No authentication/authorization layer — out of scope per the assignment; the API assumes a single trusted agent/client.
- Customers are never hard-deleted (only created/updated) — the assignment asks for "create and manage," and deleting a policyholder with a history of policies is a destructive operation a real system would likely soft-delete or block instead. No delete endpoint was added.
- A policy's `EXPIRED` status exists in the schema for completeness but nothing automatically transitions a policy to it (no background scheduler was built) — termination in this challenge happens explicitly via cancellation.
- `policy_number` is generated server-side (`POL-{year}-{random}`) and is not user-supplied.
- Email format is validated with a lightweight regex rather than pulling in the `email-validator` dependency, to keep the dependency footprint minimal.
