# Local Development Guide

## Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** — Python package manager
- **[Docker](https://docs.docker.com/get-started/get-docker/)** — required for the local PostgreSQL database

## Quick Start

```bash
# 1. Install dependencies
uv sync

# 2. Start the local database
cd local_database
docker compose up -d
cd ..

# 3. Create your .env file (see Environment Variables below)

# 4. Run the app
fastapi dev main.py
```

Then open `http://localhost:8000/api` for the interactive API docs.

## Environment Variables

Create a `.env` file in the repository root. See [ENV.md](../ENV.md) for the full reference.

### Minimum for Local Development

At minimum, you need the database connection variables:

```dotenv
POSTGRES_USER=test_source_collector_user
POSTGRES_PASSWORD=<see local_database/docker-compose.yml>
POSTGRES_DB=source_collector_test_db
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
DEV=true
```

The password and other defaults are defined in `local_database/docker-compose.yml`.

### API Keys

You'll need additional keys depending on which features you're working on:

| Variable | Required For |
|----------|-------------|
| `DS_APP_SECRET_KEY` | Any authenticated endpoint |
| `GOOGLE_API_KEY`, `GOOGLE_CSE_ID` | Auto-Googler collector |
| `DEEPSEEK_API_KEY` or `OPENAI_API_KEY` | LLM-powered tasks |
| `HUGGINGFACE_INFERENCE_API_KEY` | ML classification tasks |
| `HUGGINGFACE_HUB_TOKEN` | Uploading to HuggingFace |
| `PDAP_EMAIL`, `PDAP_PASSWORD`, `PDAP_API_KEY`, `PDAP_API_URL` | Syncing to the Data Sources App |
| `DISCORD_WEBHOOK_URL` | Error notifications |
| `INTERNET_ARCHIVE_S3_KEYS` | Internet Archive integration |

### Feature Flags

All features are enabled by default. To disable a feature during development, set its flag to `0`:

```dotenv
SCHEDULED_TASKS_FLAG=0       # Disable all scheduled tasks
POST_TO_DISCORD_FLAG=0       # Disable Discord notifications
```

See [ENV.md](../ENV.md) for the full list of flags.

## Database Setup

### Option 1: Clean Local Database

This gives you an empty database — good for running tests and isolated development.

```bash
cd local_database
docker compose up -d
```

The database schema is automatically created on app startup via Alembic migrations.

To stop the database:

```bash
cd local_database
docker compose down
```

### Option 2: Mirrored Production Database

This gives you a local copy of production data — useful for debugging or working with realistic data.

```bash
python start_mirrored_local_app.py
```

This script:
1. Starts the local database container.
2. Runs the DataDumper to pull a snapshot from production (cached for 24 hours).
3. Restores the snapshot into your local database.
4. Applies any pending Alembic migrations.
5. Starts the FastAPI server.

The mirrored approach requires additional environment variables for the production database connection. See the `Data Dumper` section in [ENV.md](../ENV.md).

## Database Migrations

This project uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations.

### Creating a New Migration

```bash
alembic revision --autogenerate -m "Description for migration"
```

Then review the generated file in `alembic/versions/` and adjust the `upgrade()` and `downgrade()` functions as needed.

### Applying Migrations

Migrations are applied automatically on app startup. To apply manually:

```bash
python apply_migrations.py
```

Or using alembic directly:

```bash
alembic upgrade head
```

See `alembic/README.md` for more details.

## Project Structure

```
.
├── src/                    # Application source code
│   ├── api/                # FastAPI routers and endpoints
│   ├── core/               # Integration layer and task system
│   ├── db/                 # Database models, client, queries
│   ├── collectors/         # URL collection strategies
│   ├── external/           # External service clients
│   ├── security/           # Authentication and authorization
│   └── util/               # Shared utilities
├── tests/                  # Test suite
├── alembic/                # Database migrations
├── local_database/         # Docker setup for local PostgreSQL
├── docs/                   # Documentation (you are here)
├── main.py                 # Alternative entry point
├── docker-compose.yml      # Test environment (app + database)
├── Dockerfile              # Production container
└── ENV.md                  # Full environment variable reference
```

## Common Workflows

### Adding a New API Endpoint

1. Create a directory under `src/api/endpoints/<group>/`.
2. Follow the existing pattern: `routes.py` for the router, subdirectories for each HTTP method.
3. Include the router in `src/api/main.py`.

### Adding a New Collector

See [collectors.md](collectors.md) for the full guide.

### Adding a New Scheduled Task

1. Create a new task operator in `src/core/tasks/scheduled/impl/`.
2. Register it in the scheduled task loader (`src/core/tasks/scheduled/loader.py`).
3. Add a corresponding flag in `EnvVarManager` and document it in `ENV.md`.

### Adding a New URL Task Operator

1. Create a new operator in `src/core/tasks/url/operators/`.
2. Register it in the URL task loader (`src/core/tasks/url/loader.py`).
3. Add a corresponding flag in `EnvVarManager` and document it in `ENV.md`.
