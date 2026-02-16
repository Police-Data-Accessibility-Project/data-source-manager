# Deployment & Migrations

## Production Container

The application is containerized using Docker and deployed to DigitalOcean.

### Dockerfile

The production image (`Dockerfile` in the repo root) is built from `python:3.11.9-slim` and includes:

- **uv** for dependency management (production deps only, no dev dependencies).
- **Playwright** with Chromium for URL screenshot capture.
- **spaCy** with the `en_core_web_sm` model for NLP-based location identification.
- Application source code, Alembic migrations, and the startup script.

The container exposes port **80**.

### Startup Process

The entrypoint runs `execute.sh`, which does two things:

1. **Applies database migrations** — runs `python apply_migrations.py`, which uses Alembic to bring the database to the latest schema version.
2. **Starts the server** — runs `uvicorn src.api.main:app --host 0.0.0.0 --port 80`.

### Environment Variables

The production container does **not** include a `.env` file (for security). Environment variables must be provided by the hosting platform. See [ENV.md](../ENV.md) for the full list.

## Database Migrations with Alembic

### Overview

[Alembic](https://alembic.sqlalchemy.org/) manages the database schema. Migration scripts live in `alembic/versions/` and are applied in order.

Key files:

| File | Purpose |
|------|---------|
| `alembic.ini` | Alembic configuration (in repo root) |
| `alembic/env.py` | Migration environment setup |
| `alembic/script.py.mako` | Template for new migration scripts |
| `alembic/versions/` | Migration scripts (40+) |
| `apply_migrations.py` | Script to apply migrations using env vars for the connection string |

### Creating a Migration

```bash
alembic revision --autogenerate -m "Description for migration"
```

This generates a new file in `alembic/versions/` based on differences between the current models and the database schema. **Always review the generated `upgrade()` and `downgrade()` functions** before committing.

### Applying Migrations

Migrations are applied automatically on every deployment (via `execute.sh`). To apply manually:

```bash
python apply_migrations.py
```

The script reads `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`, and `POSTGRES_DB` from the environment, constructs a connection string, and runs `alembic upgrade head`.

### Migration Testing

The `tests/alembic/test_revisions.py` test validates that migration scripts are well-formed. This runs in CI on every pull request.

## Data Sources App Synchronization

The Source Manager synchronizes data to the Data Sources App hourly via nine scheduled tasks. These cover three entities (agencies, data sources, meta URLs) across three operations (add, update, delete).

### How Sync Works

Each sync task:

1. Queries the SM database for entities needing sync (new entries, updated entries, or entries flagged for deletion).
2. Sends a request to the DS App endpoint at `/v3/sync/{entity}/{action}`.
3. Updates local DS App Link tables to record the sync.

### Sync Preconditions

**Add:**
- Agencies must be linked to a location.
- Data sources must be validated and linked to an agency.
- Meta URLs must be validated and linked to an agency.

**Update:**
- Triggered when relevant tables are modified (entity row, link tables, metadata).

**Delete:**
- When an entity is deleted in SM, a deletion flag is added to its DS App Link entry.
- The sync task reads these flags, sends the delete to DS, and removes the link entry.

### Sync Flags

Each sync task can be individually disabled:

```dotenv
DS_APP_SYNC_AGENCY_ADD_TASK_FLAG=0
DS_APP_SYNC_AGENCY_UPDATE_TASK_FLAG=0
DS_APP_SYNC_AGENCY_DELETE_TASK_FLAG=0
DS_APP_SYNC_DATA_SOURCE_ADD_TASK_FLAG=0
DS_APP_SYNC_DATA_SOURCE_UPDATE_TASK_FLAG=0
DS_APP_SYNC_DATA_SOURCE_DELETE_TASK_FLAG=0
DS_APP_SYNC_META_URL_ADD_TASK_FLAG=0
DS_APP_SYNC_META_URL_UPDATE_TASK_FLAG=0
DS_APP_SYNC_META_URL_DELETE_TASK_FLAG=0
```

## CI/CD Pipelines

### Test Pipeline (`.github/workflows/test_app.yml`)

Runs on every pull request:
- Spins up a PostgreSQL 15 service container.
- Installs dependencies via uv.
- Runs `pytest tests/automated` and `pytest tests/alembic`.
- 20-minute timeout.

### Lint Pipeline (`.github/workflows/python_checks.yml`)

Runs on every pull request:
- Runs flake8 via reviewdog.
- Posts advisory warnings as PR comments.
- Does **not** block merges.

Note: `python_checks.yml` only works on pull requests from branches within the repo, not from forks.
