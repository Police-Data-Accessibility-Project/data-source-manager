import re
from urllib.parse import urlparse, urlencode, parse_qs

from src.external.internet_archives.models.capture import IACapture


class InternetArchiveCDXFilter:

    @staticmethod
    def filter_by_mime_type(
        captures: list[IACapture], allowlist: list[str]
    ) -> list[IACapture]:
        return [c for c in captures if c.mimetype in allowlist]

    @staticmethod
    def filter_by_url_patterns(
        captures: list[IACapture], exclude_patterns: list[str]
    ) -> list[IACapture]:
        compiled = [re.compile(p) for p in exclude_patterns]
        return [
            c for c in captures
            if not any(regex.search(c.original) for regex in compiled)
        ]

    @staticmethod
    def _normalize_url(url: str) -> str:
        parsed = urlparse(url)
        host = parsed.hostname.lower() if parsed.hostname else ""
        path = parsed.path.rstrip("/") or "/"
        query_params = parse_qs(parsed.query)
        sorted_query = urlencode(
            sorted(
                (k, v[0]) for k, v in query_params.items()
            )
        ) if query_params else ""
        scheme = parsed.scheme or "https"
        return f"{scheme}://{host}{path}" + (
            f"?{sorted_query}" if sorted_query else ""
        )

    @staticmethod
    def deduplicate_by_url(captures: list[IACapture]) -> list[IACapture]:
        seen: dict[str, IACapture] = {}
        for capture in captures:
            normalized = InternetArchiveCDXFilter._normalize_url(
                capture.original
            )
            existing = seen.get(normalized)
            if existing is None or capture.timestamp > existing.timestamp:
                seen[normalized] = capture
        return list(seen.values())

    @staticmethod
    def filter_all(
        captures: list[IACapture],
        allowlist: list[str],
        exclude_patterns: list[str],
    ) -> list[IACapture]:
        captures = InternetArchiveCDXFilter.filter_by_mime_type(
            captures, allowlist
        )
        captures = InternetArchiveCDXFilter.filter_by_url_patterns(
            captures, exclude_patterns
        )
        captures = InternetArchiveCDXFilter.deduplicate_by_url(captures)
        return captures
