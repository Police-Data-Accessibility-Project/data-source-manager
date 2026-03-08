"""Benchmarks for the GET /annotate/all endpoint."""
import os

import pytest
from pyinstrument import Profiler
from pytest_benchmark.fixture import BenchmarkFixture

from tests.automated.integration.benchmark.scale_seed import ScaleSeedResult
from tests.automated.integration.readonly.helper import ReadOnlyTestHelper

_PROFILE_DIR = os.environ.get("PROFILE_DIR", ".")


def _save_profile(profiler: Profiler, name: str) -> None:
    """Write profiler HTML flamegraph to PROFILE_DIR."""
    path = os.path.join(_PROFILE_DIR, f"{name}.html")
    with open(path, "w") as f:
        f.write(profiler.output_html())


@pytest.mark.manual
@pytest.mark.benchmark
def test_benchmark_annotate_all_http_roundtrip(
    benchmark: BenchmarkFixture,
    benchmark_readonly_helper: ReadOnlyTestHelper,
) -> None:
    """Total HTTP round-trip time for GET /annotate/all."""
    rv = benchmark_readonly_helper
    benchmark(
        lambda: rv.api_test_helper.request_validator.get(url="/annotate/all")
    )


@pytest.mark.manual
@pytest.mark.benchmark
def test_benchmark_annotate_all_profiled(
    benchmark: BenchmarkFixture,
    benchmark_readonly_helper: ReadOnlyTestHelper,
) -> None:
    """Pyinstrument call-tree profile of GET /annotate/all (small dataset)."""
    rv = benchmark_readonly_helper
    profiler = Profiler(async_mode="enabled")

    def one_request() -> None:
        with profiler:
            rv.api_test_helper.request_validator.get(url="/annotate/all")

    benchmark(one_request)
    _save_profile(profiler, "profile_readonly")


@pytest.mark.manual
@pytest.mark.benchmark
def test_benchmark_annotate_all_scale_http_roundtrip(
    benchmark: BenchmarkFixture,
    scale_seeder: ScaleSeedResult,
) -> None:
    """Total HTTP round-trip time for GET /annotate/all at 10k-URL scale."""
    rv = scale_seeder
    benchmark(
        lambda: rv.api_test_helper.request_validator.get(url="/annotate/all")
    )


@pytest.mark.manual
@pytest.mark.benchmark
def test_benchmark_annotate_all_scale_profiled(
    benchmark: BenchmarkFixture,
    scale_seeder: ScaleSeedResult,
) -> None:
    """Pyinstrument profile of GET /annotate/all (10k-URL dataset)."""
    rv = scale_seeder
    profiler = Profiler(async_mode="enabled")

    def one_request() -> None:
        with profiler:
            rv.api_test_helper.request_validator.get(url="/annotate/all")

    benchmark(one_request)
    _save_profile(profiler, f"profile_scale_{rv.url_count}")
