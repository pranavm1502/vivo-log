# Vivo-Log

Preclinical in-vivo study and mouse colony tracking system.

## Architecture

- **Backend**: Python 3.12 / FastAPI / SQLAlchemy (async) / PostgreSQL 15
- **Frontend**: Flutter 3.x / Riverpod / Dio
- **Database migrations**: Alembic

## Prerequisites

- Python 3.12+
- Flutter 3.x
- Docker & Docker Compose

## Quick Start

The easiest way to get everything running is the single launch script:

```bash
./start.sh
```

This will start PostgreSQL, install dependencies, run migrations, launch the backend API, and open the Flutter app. When you close Flutter, the backend shuts down automatically.

### Manual Setup

If you prefer to run each step individually:

#### 1. Start the database

```bash
docker compose up -d db
```

This starts PostgreSQL 15 on port 5432 (user: `postgres`, password: `postgres`, database: `vivolog`).

#### 2. Backend setup

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

#### 3. Run migrations

```bash
alembic upgrade head
```

#### 4. Start the API server

```bash
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

#### 5. Frontend setup

```bash
cd frontend
flutter pub get
flutter run
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VIVOLOG_DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/vivolog` | Async database URL |
| `VIVOLOG_DATABASE_URL_SYNC` | `postgresql+psycopg2://postgres:postgres@localhost:5432/vivolog` | Sync database URL (Alembic) |

## Running Tests

```bash
cd backend
python -m pytest -v
```

Tests use an in-memory SQLite database — no PostgreSQL required.

## API Endpoints

### Colony Management
- `POST/GET /api/v1/colony/genotypes` — Genotype CRUD
- `POST/GET /api/v1/colony/cages` — Cage CRUD with occupancy tracking
- `POST/GET /api/v1/colony/mice` — Mouse CRUD with status/genotype filtering
- `PUT /api/v1/colony/mice/{id}/lineage` — Assign sire/dam (validates sex)
- `PUT /api/v1/colony/mice/{id}/cage` — Cage assignment (capacity check)
- `GET /api/v1/colony/mice/{id}/pedigree` — Recursive pedigree tree

### Study Management
- `POST/GET /api/v1/studies` — Study CRUD (Draft → Active → Completed)
- `POST/GET /api/v1/studies/{id}/cohorts` — Cohort management
- `POST/GET .../cohorts/{id}/enrollments` — Enroll mice (rejects deceased/culled)
- `POST/GET .../enrollments/{id}/measurements` — Record measurements

### Tumor Volume

Automatically computed as: **Volume = Length × Width² / 2**

## Project Structure

```
backend/
  app/
    main.py          # FastAPI application
    config.py        # Settings (env vars)
    database.py      # Async engine & session
    models/          # SQLAlchemy models
    schemas/         # Pydantic schemas
    routers/         # API route handlers
  alembic/           # Database migrations
  tests/             # pytest test suite
frontend/
  lib/
    main.dart        # App entry point
    api/             # Dio HTTP client & repositories
    models/          # Dart data classes
    providers/       # Riverpod state providers
    screens/         # UI screens (colony & study)
    widgets/         # Reusable widgets
```

## License

See [LICENSE](LICENSE).
