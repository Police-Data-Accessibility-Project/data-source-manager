# API Reference

The Source Manager exposes a FastAPI application with 15 route groups and 65 endpoints. The interactive API docs are available at `/api` when the server is running.

## Authentication

Most endpoints require a valid Bearer token from the [Data Sources App](https://data-sources.pdap.io/api). Tokens are JWTs validated against the `DS_APP_SECRET_KEY` environment variable.

Two permission levels are used:

| Permission | Description |
|------------|-------------|
| `access_source_collector` | General access (required for most endpoints) |
| `source_collector_final_review` | Final review of annotations |

Include the token in the `Authorization` header:

```
Authorization: Bearer <token>
```

## Endpoints

### Root (`/`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Health check — returns "Hello World" |

---

### Agencies (`/agencies`)

Manage agencies and their location associations.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/agencies` | List agencies (paginated) |
| POST | `/agencies` | Create a new agency |
| DELETE | `/agencies/{agency_id}` | Delete an agency |
| PUT | `/agencies/{agency_id}` | Update an agency |
| GET | `/agencies/{agency_id}/locations` | List locations for an agency |
| POST | `/agencies/{agency_id}/locations/{location_id}` | Link a location to an agency |
| DELETE | `/agencies/{agency_id}/locations/{location_id}` | Unlink a location from an agency |

---

### Annotate (`/annotate`)

Annotation workflows for labeling URLs — both anonymous and authenticated.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/annotate/anonymous` | Get next URL for anonymous annotation |
| POST | `/annotate/anonymous/{url_id}` | Submit anonymous annotation, get next URL |
| GET | `/annotate/all` | Get next URL for authenticated annotation (optional `batch_id`, `url_id` filters) |
| POST | `/annotate/all/{url_id}` | Submit authenticated annotation, get next URL |
| GET | `/annotate/suggestions/agencies/{url_id}` | Get agency suggestions for a URL |

---

### Batch (`/batch`)

View and manage URL collection batches.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/batch` | List batch summaries (filterable by collector type, status) |
| GET | `/batch/{batch_id}` | Get batch details |
| GET | `/batch/{batch_id}/urls` | List URLs in a batch (paginated) |
| GET | `/batch/{batch_id}/duplicates` | List duplicate URLs in a batch (paginated) |
| GET | `/batch/{batch_id}/logs` | Get logs for a batch |
| POST | `/batch/{batch_id}/abort` | Abort a running batch |

---

### Check (`/check`)

Validation endpoints.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/check/unique-url` | Check if a URL is unique in the database |

---

### Collector (`/collector`)

Start URL collection runs. Each collector type has its own endpoint.

| Method | Path | Description |
|--------|------|-------------|
| POST | `/collector/example` | Start the example collector |
| POST | `/collector/ckan` | Start the CKAN collector |
| POST | `/collector/common-crawler` | Start the Common Crawler collector |
| POST | `/collector/auto-googler` | Start the Auto Googler collector |
| POST | `/collector/muckrock-simple` | Start MuckRock simple search |
| POST | `/collector/muckrock-county` | Start MuckRock county-level search |
| POST | `/collector/muckrock-all` | Start MuckRock all FOIA requests |
| POST | `/collector/manual` | Upload a manual batch of URLs |

---

### Contributions (`/contributions`)

Track user annotation contributions.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/contributions/leaderboard` | Get contribution leaderboard |
| GET | `/contributions/user` | Get current user's contributions and agreement rates |

---

### Data Sources (`/data-sources`)

Manage validated data sources and their agency associations.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/data-sources` | List data sources (paginated) |
| GET | `/data-sources/{url_id}` | Get a data source by URL ID |
| PUT | `/data-sources/{url_id}` | Update a data source |
| GET | `/data-sources/{url_id}/agencies` | List agencies for a data source |
| POST | `/data-sources/{url_id}/agencies/{agency_id}` | Link an agency to a data source |
| DELETE | `/data-sources/{url_id}/agencies/{agency_id}` | Unlink an agency from a data source |

---

### Locations (`/locations`)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/locations` | Create a new location |

---

### Meta URLs (`/meta-urls`)

Manage meta URLs (non-data-source URLs associated with agencies) and their agency associations.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/meta-urls` | List meta URLs (paginated) |
| PUT | `/meta-urls/{url_id}` | Update a meta URL |
| GET | `/meta-urls/{url_id}/agencies` | List agencies for a meta URL |
| POST | `/meta-urls/{url_id}/agencies/{agency_id}` | Link an agency to a meta URL |
| DELETE | `/meta-urls/{url_id}/agencies/{agency_id}` | Unlink an agency from a meta URL |

---

### Metrics (`/metrics`)

Analytics and progress tracking.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/metrics/batches/aggregated` | Aggregated batch metrics |
| GET | `/metrics/batches/breakdown` | Per-batch metrics breakdown (paginated) |
| GET | `/metrics/urls/aggregate` | Aggregated URL metrics |
| GET | `/metrics/urls/aggregate/pending` | Aggregated pending URL metrics |
| GET | `/metrics/urls/breakdown/submitted` | Submitted URLs breakdown |
| GET | `/metrics/urls/breakdown/pending` | Pending URLs breakdown |
| GET | `/metrics/backlog` | Annotation backlog metrics |

---

### Search (`/search`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/search/url` | Search for a URL |
| GET | `/search/agency` | Search for agencies (requires at least one of: `query`, `location_id`, `jurisdiction_type`) |

---

### Submit (`/submit`)

Submit new URLs and data sources for review.

| Method | Path | Description |
|--------|------|-------------|
| POST | `/submit/url` | Submit a URL for review |
| POST | `/submit/data-source` | Submit a data source proposal (returns 409 if duplicate) |

---

### Task (`/task`)

View task status and history.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/task` | List tasks (filterable by status and type, paginated) |
| GET | `/task/status` | Get current task processing status |
| GET | `/task/{task_id}` | Get details for a specific task |

---

### URL (`/url`)

View and manage individual URLs.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/url` | List URLs (paginated, filterable to show errors only) |
| GET | `/url/{url_id}/screenshot` | Get screenshot for a URL (returns WebP image) |
| DELETE | `/url/{url_id}` | Delete a URL |

## Endpoint Structure

Each endpoint group follows a consistent directory layout:

```
src/api/endpoints/<group>/
├── routes.py               # APIRouter definition with all routes
├── get/                    # GET endpoint(s)
│   ├── __init__.py         # Handler function
│   ├── query.py            # Database query logic
│   └── dto.py / response.py / request.py
├── post/                   # POST endpoint(s)
├── put/                    # PUT endpoint(s)
├── delete/                 # DELETE endpoint(s)
└── _shared/                # Shared logic across HTTP methods
```

## CORS

Allowed origins:

- `http://localhost:8888` (local development)
- `https://pdap.io`
- `https://pdap.dev`
