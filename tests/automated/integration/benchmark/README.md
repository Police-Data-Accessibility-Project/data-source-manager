# Annotation Load Time Benchmarks

Baseline benchmarks for the `GET /annotate/all` endpoint (issue #566).
Run manually or via the [`benchmark` GHA workflow](../../../../.github/workflows/benchmark.yml).

## What is measured

```mermaid
sequenceDiagram
    participant C as Test Client
    participant R as routes.py
    participant Q as GetNextURLForAllAnnotation<br/>QueryBuilder
    participant E as extract_and_format_<br/>get_annotation_result()
    participant DB as Database

    C->>R: GET /annotate/all
    note over C,R: ← total HTTP round-trip (test_benchmark_annotate_all_http_roundtrip)

    R->>Q: get_next_url_for_all_annotations()

    rect rgb(220, 235, 255)
        note right of Q: _phase("main_query_s")
        Q->>DB: SELECT url … JOIN materialized views (CTE)
        DB-->>Q: URL row
    end

    Q->>E: extract_and_format_get_annotation_result(url)

    rect rgb(220, 255, 220)
        note right of E: _phase("format_s")
        E->>E: html / url_type / record_type conversions<br/>(eager-loaded, no extra query)
    end

    rect rgb(220, 235, 255)
        note right of E: _phase("agency_suggestions_s")
        E->>DB: GetAgencySuggestionsQueryBuilder
        DB-->>E: agency rows
    end

    rect rgb(220, 235, 255)
        note right of E: _phase("location_suggestions_s")
        E->>DB: GetLocationSuggestionsQueryBuilder
        DB-->>E: location rows
    end

    rect rgb(220, 235, 255)
        note right of E: _phase("name_suggestions_s")
        E->>DB: GetNameSuggestionsQueryBuilder
        DB-->>E: name rows
    end

    rect rgb(220, 235, 255)
        note right of E: _phase("batch_info_s")
        E->>DB: GetAnnotationBatchInfoQueryBuilder
        DB-->>E: batch info
    end

    E-->>R: GetNextURLForAllAnnotationResponse
    R-->>C: 200 OK
```

Each shaded block corresponds to a `_phase()` context manager in the source.
The per-phase timings are collected via `AnnotationTimings` / `collect_timings()`
from `src/api/endpoints/annotate/_shared/timing.py` — zero-cost in production
when no collector is active.

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
