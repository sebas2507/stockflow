# StockFlow

Inventory management API with automated restock requests and a **human-in-the-loop approval workflow**.

Built to replace a manual Excel-based inventory process at a distribution company: 214 products across 7 product families, with stock status typed by hand and no history of changes.

## Features

- **Products** organized by family, with stock status (`OK`, `LOW STOCK`, `OUT OF STOCK`) **calculated**, not typed by hand.
- **Stock movements** (IN/OUT) as an audit trail. Stock is never edited directly.
- **Automatic restock requests** when stock falls below the minimum (quantity = 2 × minimum − current stock), without duplicates.
- **Approval workflow:** `PENDING → APPROVED / REJECTED`. Rejections require a comment.
- **Batch job** that scans the whole inventory and creates the missing requests (idempotent).
- **Concurrency-safe:** row-level locking (`SELECT ... FOR UPDATE`) prevents race conditions on simultaneous stock-outs.

## Tech Stack

| Layer | Technology |
|---|---|
| API | Python 3.14, FastAPI, Pydantic |
| Database | PostgreSQL 17, SQLAlchemy 2.0 (ORM), psycopg |
| Infrastructure | Docker, Docker Compose |
| Testing | pytest, FastAPI TestClient, isolated test database |

## Architecture

```
Client (Swagger / Frontend)
        │  HTTP / JSON
        ▼
   main.py        → Endpoints: receive request, call service, return response
        │
   services.py    → Business rules: movements, restock logic, state machine
        │
   models.py      → SQLAlchemy models (tables)
        │
   PostgreSQL (Docker)
```

- `schemas.py` defines the API contract (input/output validation with Pydantic), separate from the database models.
- Business errors (`NotFound`, `Conflict`) are mapped to HTTP status codes (404, 409) in one place with exception handlers.

## Getting Started

**Requirements:** Python 3.12+, Docker Desktop, Git.

```bash
git clone https://github.com/sebas2507/stockflow.git
cd stockflow

python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt

cp .env.example .env            # then set your own password
docker compose up -d            # starts PostgreSQL
python -m app.seed              # creates tables and sample data
fastapi dev app/main.py
```

Open the interactive API docs at **http://127.0.0.1:8000/docs**.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/products?familia=&estado=` | List products, with optional filters |
| GET | `/products/{id}` | Get one product |
| POST | `/products` | Create a product |
| POST | `/products/{id}/movements` | Register a stock IN/OUT |
| GET | `/products/{id}/movements` | Movement history |
| GET | `/restock-requests?estado=` | List restock requests |
| POST | `/restock-requests/generate` | Scan inventory and create missing requests |
| POST | `/restock-requests/{id}/approve` | Approve a pending request |
| POST | `/restock-requests/{id}/reject` | Reject a pending request (comment required) |

## Running Tests

```bash
docker exec -it stockflow-db psql -U stockflow -d stockflow -c "CREATE DATABASE stockflow_test;"
pytest -v
```

Unit tests cover the business rules, including boundary values. Integration tests call the API against an isolated PostgreSQL test database that is recreated for each test.

## Design Decisions

- **Derived data isn't stored:** stock status is calculated from stock and minimum, so it can never get out of sync.
- **Movements + current stock** are updated in the same transaction: fast reads with a full audit trail.
- **Approving a request doesn't change stock:** stock increases when the goods actually arrive (an IN movement), matching the real process.
- **Rejected requests** can be recreated by the batch job if the product is still below the minimum. A cooldown period is a possible future improvement.

## Roadmap

- [ ] Run the API in Docker (full `docker compose up`)
- [ ] React + TypeScript frontend
- [ ] CI with GitHub Actions
- [ ] Database migrations with Alembic
- [ ] Authentication and roles (operator / supervisor)