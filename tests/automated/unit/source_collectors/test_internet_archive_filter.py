from src.collectors.impl.internet_archive.filter import InternetArchiveCDXFilter
from src.external.internet_archives.models.capture import IACapture


def _capture(
    url: str,
    mimetype: str = "text/html",
    timestamp: int = 20240101000000,
    digest: str = "abc123",
    length: int = 1000,
) -> IACapture:
    return IACapture(
        original=url,
        mimetype=mimetype,
        timestamp=timestamp,
        digest=digest,
        length=length,
    )


class TestFilterByMimeType:

    def test_keeps_allowed_types(self):
        captures = [
            _capture("http://example.com/page", mimetype="text/html"),
            _capture("http://example.com/style.css", mimetype="text/css"),
            _capture("http://example.com/image.png", mimetype="image/png"),
        ]
        result = InternetArchiveCDXFilter.filter_by_mime_type(
            captures, ["text/html"]
        )
        assert len(result) == 1
        assert result[0].original == "http://example.com/page"

    def test_multiple_allowed_types(self):
        captures = [
            _capture("http://example.com/page", mimetype="text/html"),
            _capture("http://example.com/doc.pdf", mimetype="application/pdf"),
            _capture("http://example.com/style.css", mimetype="text/css"),
        ]
        result = InternetArchiveCDXFilter.filter_by_mime_type(
            captures, ["text/html", "application/pdf"]
        )
        assert len(result) == 2

    def test_empty_captures(self):
        result = InternetArchiveCDXFilter.filter_by_mime_type(
            [], ["text/html"]
        )
        assert result == []


class TestFilterByURLPatterns:

    def test_excludes_static_assets(self):
        captures = [
            _capture("http://example.com/page"),
            _capture("http://example.com/style.css"),
            _capture("http://example.com/script.js"),
            _capture("http://example.com/image.png"),
        ]
        result = InternetArchiveCDXFilter.filter_by_url_patterns(
            captures, [r"\.css$", r"\.js$", r"\.png$"]
        )
        assert len(result) == 1
        assert result[0].original == "http://example.com/page"

    def test_excludes_cms_paths(self):
        captures = [
            _capture("http://example.com/page"),
            _capture("http://example.com/wp-content/uploads/file.pdf"),
            _capture("http://example.com/wp-includes/js/jquery.js"),
        ]
        result = InternetArchiveCDXFilter.filter_by_url_patterns(
            captures, [r"/wp-content/", r"/wp-includes/"]
        )
        assert len(result) == 1

    def test_excludes_tracking_params(self):
        captures = [
            _capture("http://example.com/page"),
            _capture("http://example.com/page?utm_source=twitter"),
            _capture("http://example.com/page?fbclid=abc123"),
        ]
        result = InternetArchiveCDXFilter.filter_by_url_patterns(
            captures, [r"utm_", r"fbclid"]
        )
        assert len(result) == 1


class TestDeduplicateByURL:

    def test_keeps_latest_capture(self):
        captures = [
            _capture("http://example.com/page", timestamp=20230101000000),
            _capture("http://example.com/page", timestamp=20240101000000),
        ]
        result = InternetArchiveCDXFilter.deduplicate_by_url(captures)
        assert len(result) == 1
        assert result[0].timestamp == 20240101000000

    def test_normalizes_trailing_slash(self):
        captures = [
            _capture("http://example.com/page", timestamp=20230101000000),
            _capture("http://example.com/page/", timestamp=20240101000000),
        ]
        result = InternetArchiveCDXFilter.deduplicate_by_url(captures)
        assert len(result) == 1

    def test_normalizes_case(self):
        captures = [
            _capture("http://Example.COM/page", timestamp=20230101000000),
            _capture("http://example.com/page", timestamp=20240101000000),
        ]
        result = InternetArchiveCDXFilter.deduplicate_by_url(captures)
        assert len(result) == 1

    def test_normalizes_fragments_ignored(self):
        captures = [
            _capture("http://example.com/page#section1"),
            _capture("http://example.com/page#section2"),
        ]
        result = InternetArchiveCDXFilter.deduplicate_by_url(captures)
        assert len(result) == 1

    def test_sorts_query_params(self):
        captures = [
            _capture(
                "http://example.com/page?b=2&a=1", timestamp=20230101000000
            ),
            _capture(
                "http://example.com/page?a=1&b=2", timestamp=20240101000000
            ),
        ]
        result = InternetArchiveCDXFilter.deduplicate_by_url(captures)
        assert len(result) == 1


class TestFilterAll:

    def test_end_to_end(self):
        captures = [
            _capture("http://example.com/page", mimetype="text/html"),
            _capture("http://example.com/style.css", mimetype="text/css"),
            _capture(
                "http://example.com/page",
                mimetype="text/html",
                timestamp=20250101000000,
            ),
            _capture(
                "http://example.com/wp-content/upload",
                mimetype="text/html",
            ),
        ]
        result = InternetArchiveCDXFilter.filter_all(
            captures,
            allowlist=["text/html"],
            exclude_patterns=[r"/wp-content/"],
        )
        assert len(result) == 1
        assert result[0].timestamp == 20250101000000
