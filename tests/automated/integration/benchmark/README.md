# Annotation Load Time Benchmarks

Benchmarks for the `GET /annotate/all` endpoint.
Run manually or via the [`benchmark` GHA workflow](../../../../.github/workflows/benchmark.yml).

## What is measured

Each benchmark hits `GET /annotate/all` and records either the total HTTP round-trip
or a pyinstrument call-tree profile.

Two fixture sizes are used:

| Fixture | Description |
|---|---|
| `benchmark_readonly_helper` | Small realistic dataset |
| `scale_seeder` | 10 000-URL dataset to surface query scaling behaviour |

## Tests

| Test | What it measures |
|---|---|
| `test_benchmark_annotate_all_http_roundtrip` | Total HTTP round-trip time (small dataset) |
| `test_benchmark_annotate_all_profiled` | pyinstrument flamegraph (small dataset) |
| `test_benchmark_annotate_all_scale_http_roundtrip` | Total HTTP round-trip time (10k-URL dataset) |
| `test_benchmark_annotate_all_scale_profiled` | pyinstrument flamegraph (10k-URL dataset) |

## Profiled tests

The `_profiled` tests wrap each benchmark round with a `pyinstrument.Profiler`
(`async_mode="enabled"`) so that time is attributed correctly across `await` boundaries.
After all rounds complete, they write a self-contained interactive HTML flamegraph to
`$PROFILE_DIR` (defaults to the current directory):

- `profile_readonly.html`
- `profile_scale_{url_count}.html`

Open these files in any browser — no extra tooling required.

## Running locally

Set the required environment variables (see [`ENV.md`](../../../../ENV.md) for values),
then run:

```bash
PROFILE_DIR=. uv run pytest tests/automated/integration/benchmark \
  -m "manual and benchmark" \
  --benchmark-json=benchmark-results.json \
  -v
```

## Comparing runs

```bash
uv run pytest-benchmark compare baseline.json new-results.json --sort=mean
```
