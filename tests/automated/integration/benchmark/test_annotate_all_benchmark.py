import json
import os

import pytest

from src.api.endpoints.annotate._shared.timing import AnnotationTimings, collect_timings

_PHASE_ATTRS = (
    "main_query_s",
    "agency_suggestions_s",
    "location_suggestions_s",
    "name_suggestions_s",
    "batch_info_s",
    "format_s",
)
_PER_PHASE_FILE = os.environ.get("PER_PHASE_JSON", "per-phase-results.json")


def _write_per_phase(key: str, all_timings: list[AnnotationTimings]) -> None:
    n = len(all_timings)
    if not n:
        return
    averages = {attr: sum(getattr(t, attr) for t in all_timings) / n for attr in _PHASE_ATTRS}
    try:
        with open(_PER_PHASE_FILE) as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data[key] = averages
    with open(_PER_PHASE_FILE, "w") as f:
        json.dump(data, f, indent=2)


@pytest.mark.manual
@pytest.mark.benchmark
def test_benchmark_annotate_all_http_roundtrip(benchmark, benchmark_readonly_helper):
    """Total HTTP round-trip time for GET /annotate/all."""
    rv = benchmark_readonly_helper
    benchmark(lambda: rv.api_test_helper.request_validator.get(url="/annotate/all"))


@pytest.mark.manual
@pytest.mark.benchmark
def test_benchmark_annotate_all_per_phase(benchmark, benchmark_readonly_helper):
    """Per-phase server-side timing breakdown."""
    rv = benchmark_readonly_helper
    all_timings = []

    def one_request():
        collector = AnnotationTimings()
        with collect_timings(collector):
            rv.api_test_helper.request_validator.get(url="/annotate/all")
        all_timings.append(collector)

    benchmark(one_request)

    _write_per_phase("readonly", all_timings)


@pytest.mark.manual
@pytest.mark.benchmark
def test_benchmark_annotate_all_scale_http_roundtrip(benchmark, scale_seeder):
    """Total HTTP round-trip time for GET /annotate/all against 10k-URL dataset."""
    rv = scale_seeder
    benchmark(lambda: rv.api_test_helper.request_validator.get(url="/annotate/all"))


@pytest.mark.manual
@pytest.mark.benchmark
def test_benchmark_annotate_all_scale_per_phase(benchmark, scale_seeder):
    """Per-phase server-side timing breakdown against 10k-URL dataset."""
    rv = scale_seeder
    all_timings = []

    def one_request():
        collector = AnnotationTimings()
        with collect_timings(collector):
            rv.api_test_helper.request_validator.get(url="/annotate/all")
        all_timings.append(collector)

    benchmark(one_request)

    _write_per_phase(f"scale_{rv.url_count}", all_timings)
