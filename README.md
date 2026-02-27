# Data Source Manager

A FastAPI application for identifying and cataloguing police data sources. Part of the [Police Data Accessibility Project](https://pdap.io) (PDAP).

The Source Manager collects URLs from various sources, enriches them with metadata using automated tasks and ML models, supports human annotation for validation, and synchronizes approved data sources to the [Data Sources App](https://data-sources.pdap.io/api).

## Quick Start

```bash
# Install dependencies
uv sync

# Start the local database
cd local_database && docker compose up -d && cd ..

# Create a .env file (see ENV.md for all variables)
# At minimum, set the POSTGRES_* variables to match local_database defaults.

# Run the app
fastapi dev main.py
```

Then open `http://localhost:8000/api` for the interactive API docs.

Note: accessing API endpoints requires a valid Bearer token from the Data Sources API.

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/architecture.md) | System design, module structure, task system, data flow |
| [API Reference](docs/api.md) | All 65 endpoints across 15 route groups |
| [Development Guide](docs/development.md) | Local setup, environment variables, common workflows |
| [Testing Guide](docs/testing.md) | Running tests, CI pipeline, writing new tests |
| [Deployment](docs/deployment.md) | Docker, Alembic migrations, DS App synchronization |
| [Collectors](docs/collectors.md) | Collector architecture and how to build new ones |
| [Environment Variables](ENV.md) | Full reference for all env vars and feature flags |

## Project Structure

```
src/
├── api/            # FastAPI routers and endpoint logic
├── core/           # Integration layer and task system
├── db/             # SQLAlchemy models, async DB client, queries
├── collectors/     # Pluggable URL collection strategies
├── external/       # Clients for external services (HuggingFace, PDAP, etc.)
├── security/       # JWT auth and permissions
└── util/           # Shared helpers
```

## Contributing

Thank you for your interest in contributing to this project! Please follow these guidelines:

- [These Design Principles](https://github.com/Police-Data-Accessibility-Project/meta/blob/main/DESIGN-PRINCIPLES.md) may be used to make decisions or guide your work.
- If you want to work on something, create an issue first so the broader community can discuss it.
- If you make a utility, script, app, or other useful bit of code: put it in a top-level directory with an appropriate name and dedicated README and add it to the index.

## Code Quality

Linting runs via flake8 in GitHub Actions (`python_checks.yml`) and posts advisory review comments (non-blocking).

To run the same lint checks before committing, install and use the `prek` pre-commit hook runner:

```bash
uv sync --group dev
uv run prek install

# run hooks on all files
uv run prek run --all-files
```

Note: `python_checks.yml` only runs on pull requests from within the repo, not from forks.
