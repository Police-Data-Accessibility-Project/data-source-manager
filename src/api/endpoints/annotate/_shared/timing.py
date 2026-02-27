import time
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Iterator


@dataclass
class AnnotationTimings:
    """Per-phase server-side timing data for GET /annotate/all.

    All values are in seconds.
    """

    main_query_s: float = 0.0
    agency_suggestions_s: float = 0.0
    location_suggestions_s: float = 0.0
    name_suggestions_s: float = 0.0
    batch_info_s: float = 0.0
    format_s: float = 0.0


_active_collector: ContextVar["AnnotationTimings | None"] = ContextVar(
    "_active_collector", default=None
)


@contextmanager
def collect_timings(
    collector: AnnotationTimings,
) -> Iterator[AnnotationTimings]:
    """Activate *collector* so that _phase() calls record into it."""
    token = _active_collector.set(collector)
    try:
        yield collector
    finally:
        _active_collector.reset(token)


@contextmanager
def _phase(attr: str) -> Iterator[None]:
    collector = _active_collector.get()
    t0 = time.perf_counter()
    yield
    elapsed = time.perf_counter() - t0
    if collector is not None:
        setattr(collector, attr, elapsed)
