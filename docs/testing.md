# Testing Guide

## Prerequisites

- **Docker** must be installed and the Docker engine must be running.
- **uv** for dependency management.

## Test Categories

Tests are organized into three categories:

### Automated Tests (`tests/automated/`)

These run in CI and do not call any third-party APIs. They include:

- **Integration tests** — API endpoints, database operations, core functionality, security, and tasks.
- **Unit tests** — isolated logic tests.

### Alembic Tests (`tests/alembic/`)

Validates that database migration scripts are well-formed and can be applied cleanly.

### Manual Tests (`tests/manual/`)

Tests that call third-party APIs (Google, MuckRock, etc.) and are **not** run automatically. The directory intentionally lacks the `test` prefix to prevent accidental inclusion in pytest runs.

Run these individually and only when needed — they may incur API costs.

## Running Tests Locally

### Option 1: Direct (Recommended for Development)

Start the local database, then run pytest:

```bash
# Start the database
cd local_database
docker compose up -d
cd ..

# Run automated tests
uv run pytest tests/automated

# Run alembic tests
uv run pytest tests/alembic
```

### Option 2: Docker Compose (Matches CI)

This spins up a two-container setup (FastAPI app + PostgreSQL):

```bash
docker compose up -d
```

Then run tests inside the container:

```bash
docker exec data-source-identification-app-1 pytest /app/tests/automated
```

**Note:** The `docker-compose.yml` in the root is configured for Linux Docker (used in GitHub Actions). For local development on Windows/macOS, you may need to change `POSTGRES_HOST` from `172.17.0.1` to `host.docker.internal`. See the comments in `docker-compose.yml`.

## CI Pipeline

The GitHub Actions workflow (`.github/workflows/test_app.yml`) runs on every pull request:

1. Starts a PostgreSQL 15 service container with health checks.
2. Installs uv and project dependencies.
3. Runs `pytest tests/automated`.
4. Runs `pytest tests/alembic`.

The pipeline has a 20-minute timeout.

A separate workflow (`.github/workflows/python_checks.yml`) runs flake8 linting via reviewdog on pull requests. These are advisory warnings and do not block merges.

## Test Structure

```
tests/
├── conftest.py             # Session fixtures: DB setup, teardown, client instances
├── helpers/
│   ├── alembic_runner.py   # Alembic test utilities
│   ├── data_creator/       # Test data generation helpers
│   └── setup/              # Database populate/wipe utilities
├── test_data/              # Static test data (JSON files, etc.)
├── automated/
│   ├── integration/
│   │   ├── api/            # Endpoint tests (agencies, annotate, batch, etc.)
│   │   ├── core/           # Core async operation tests
│   │   ├── db/
│   │   │   ├── client/     # Database client method tests
│   │   │   └── structure/  # Schema validation tests
│   │   ├── readonly/       # Read-only operation tests
│   │   ├── security_manager/  # Auth/authz tests
│   │   └── tasks/          # Task implementation tests
│   └── unit/               # Unit tests
├── alembic/
│   └── test_revisions.py   # Migration validation
└── manual/
    ├── core/lifecycle/     # Core lifecycle tests
    ├── source_collectors/  # Collector integration tests
    └── unsorted/           # Miscellaneous manual tests
```

## Test Configuration

From `pytest.ini`:

- **Timeout:** 300 seconds per test.
- **Async mode:** `auto` (all async tests are automatically detected).
- **Fixture loop scope:** `function` (each test gets its own event loop).
- **Manual tests** are marked and excluded from automated runs.

## Writing New Tests

- Place automated tests in `tests/automated/integration/` or `tests/automated/unit/`.
- Use the fixtures defined in `conftest.py` for database access (`adb_client`, `db_client`).
- Use helpers in `tests/helpers/data_creator/` to generate test data.
- If your test calls a third-party API, place it in `tests/manual/` and do **not** prefix the directory with `test`.
