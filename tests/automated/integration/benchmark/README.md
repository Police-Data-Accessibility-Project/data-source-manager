# Annotation Load Time Benchmarks

Benchmarks for the `GET /annotate/all` endpoint.
Run manually or via the [`benchmark` GHA workflow](../../../../.github/workflows/benchmark.yml).

## What is measured

Each benchmark hits `GET /annotate/all` and records either the total HTTP round-trip
or a per-phase server-side breakdown.

A **phase** is a named segment of the server-side request pipeline — one logical unit
of work (e.g. a database query or serialisation step) whose duration is tracked
independently. Phases are instrumented via `_phase()` context managers placed directly
in the source code; the canonical list of phase names and their dataclass fields lives in
[`src/api/endpoints/annotate/_shared/timing.py`](../../../../src/api/endpoints/annotate/_shared/timing.py).

| Phase | What it measures |
|---|---|
| `main_query` | SELECT to fetch the next URL and its annotation state |
| `agency_suggestions` | Agency suggestion query |
| `location_suggestions` | Location suggestion query |
| `name_suggestions` | Name suggestion query |
| `batch_info` | Annotation batch metadata query |
| `format` | Response serialisation (no DB query) |

Two fixture sizes are used:

| Fixture | Description |
|---|---|
| `benchmark_readonly_helper` | Small realistic dataset |
| `scale_seeder` | 10 000-URL dataset to surface query scaling behaviour |

## Running locally

Set the required environment variables (see [`ENV.md`](../../../../ENV.md) for values),
then run:

```bash
uv run pytest tests/automated/integration/benchmark \
  -m "manual and benchmark" \
  --benchmark-json=benchmark-results.json \
  -v
```

## Comparing runs

```bash
uv run pytest-benchmark compare baseline.json new-results.json --sort=mean
```
