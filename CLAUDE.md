# CLAUDE.md

This file provides context for Claude Code when working in this repository.

## Project Overview

This is the **Source Manager** — a FastAPI application for the Police Data Accessibility Project (PDAP). It collects, enriches, and manages URLs that point to police data sources, then synchronizes validated results to the Data Sources App.

## Tech Stack

- **Python 3.11+** with **uv** for package management
- **FastAPI** + **uvicorn** for the web framework
- **SQLAlchemy** (async) + **asyncpg** for database access
- **PostgreSQL 15** as the database
- **Alembic** for database migrations
- **Pydantic v2** for data validation
- **Docker** for local database and testing
- **pytest** + **pytest-asyncio** for testing

## Key Commands

```bash
# Install dependencies
uv sync

# Start local database
cd local_database && docker compose up -d && cd ..

# Run the app locally
fastapi dev main.py

# Run automated tests (requires local database running)
uv run pytest tests/automated

# Run alembic migration tests
uv run pytest tests/alembic

# Generate a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations manually
python apply_migrations.py
```

## Project Structure

All application code lives under `src/`:

- `src/api/` — FastAPI routers and endpoints (15 route groups, 65 endpoints)
- `src/core/` — Integration layer: `AsyncCore`, task system, logger, env var manager
- `src/db/` — Database layer: async client, SQLAlchemy models, queries, DTOs
- `src/collectors/` — Pluggable URL collectors (Common Crawler, Auto-Googler, CKAN, MuckRock)
- `src/external/` — External service clients (HuggingFace, PDAP API, Internet Archive)
- `src/security/` — JWT auth via tokens from the Data Sources App
- `src/util/` — Shared helper functions

## Architecture Patterns

### API Endpoint Convention

Each endpoint group follows this layout:

```
src/api/endpoints/<group>/
├── routes.py           # APIRouter with all routes
├── get/ post/ put/ delete/
│   ├── __init__.py     # Endpoint handler
│   ├── query.py        # Database query logic
│   └── dto.py          # Request/response Pydantic models
└── _shared/            # Shared logic across methods
```

### Dependency Injection

The app uses FastAPI's `app.state` to share core dependencies:
- `app.state.async_core` — `AsyncCore` instance (main facade)
- `app.state.async_scheduled_task_manager` — scheduled task manager
- `app.state.logger` — `AsyncCoreLogger` instance

### Collector Pattern

All collectors inherit from `AsyncCollectorBase` and are registered in `src/collectors/mapping.py`. Each must implement `run_implementation()` and specify a `preprocessor` class.

### Task System

- **URL tasks** enrich individual URLs (HTML scraping, agency ID, record type classification, etc.). Operators live in `src/core/tasks/url/operators/`.
- **Scheduled tasks** handle system-wide operations (sync to DS App, cleanup, HuggingFace upload, etc.). Implementations live in `src/core/tasks/scheduled/impl/`.

## Testing

- **Automated tests** (`tests/automated/`) — run in CI, no third-party API calls.
- **Alembic tests** (`tests/alembic/`) — validate migration scripts.
- **Manual tests** (`tests/manual/`) — involve third-party APIs, run individually. Directory lacks `test` prefix intentionally.
- Async mode is `auto` — async test functions are detected automatically.
- Test timeout is 300 seconds.
- Fixtures in `tests/conftest.py` provide `adb_client` and `db_client`.
- Test data helpers are in `tests/helpers/data_creator/`.

## Environment Variables

See `ENV.md` for the full reference. Key categories:
- `POSTGRES_*` — database connection
- `DS_APP_SECRET_KEY` — JWT validation (must match the Data Sources App)
- Various API keys (Google, HuggingFace, PDAP, Discord, etc.)
- Feature flags — all tasks can be individually toggled (set to `0` to disable)

## Database

- Managed with Alembic. Migrations live in `alembic/versions/`.
- Models are in `src/db/models/impl/` organized by entity.
- The primary interface is `AsyncDatabaseClient` in `src/db/client/async_.py`.
- Local database uses Docker: `local_database/docker-compose.yml`.

## Important Notes

- The app exposes its API docs at `/api` (not the default `/docs` — `/docs` redirects to `/api`).
- CORS is configured for `localhost:8888`, `pdap.io`, and `pdap.dev`.
- Two permission levels: `access_source_collector` (general) and `source_collector_final_review` (final review).
- The app synchronizes agencies, data sources, and meta URLs to the Data Sources App via nine scheduled sync tasks.
