"""Tests for the Internet Archive CDX filter."""
from src.collectors.impl.internet_archive.filter import InternetArchiveCDXFilter
from src.external.internet_archives.models.capture import IACapture


def _capture(
    url: str,
    mimetype: str = "text/html",
    timestamp: int = 20240101000000,
    digest: str = "abc123",
    length: int = 1000,
) -> IACapture:
    """Create an IACapture for testing."""
    return IACapture(
        original=url,
        mimetype=mimetype,
        timestamp=timestamp,
        digest=digest,
        length=length,
    )


class TestFilterByMimeType:
    """Tests for MIME type filtering."""

    def test_keeps_allowed_types(self: "TestFilterByMimeType") -> None:
        """Test that only allowed MIME types are kept."""
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

    def test_multiple_allowed_types(self: "TestFilterByMimeType") -> None:
        """Test filtering with multiple allowed MIME types."""
        captures = [
            _capture("http://example.com/page", mimetype="text/html"),
            _capture("http://example.com/doc.pdf", mimetype="application/pdf"),
            _capture("http://example.com/style.css", mimetype="text/css"),
        ]
        result = InternetArchiveCDXFilter.filter_by_mime_type(
            captures, ["text/html", "application/pdf"]
        )
        assert len(result) == 2

    def test_empty_captures(self: "TestFilterByMimeType") -> None:
        """Test filtering an empty list returns empty."""
        result = InternetArchiveCDXFilter.filter_by_mime_type(
            [], ["text/html"]
        )
        assert result == []


class TestFilterByURLPatterns:
    """Tests for URL pattern exclusion filtering."""

    def test_excludes_static_assets(self: "TestFilterByURLPatterns") -> None:
        """Test that static asset URLs are excluded."""
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

    def test_excludes_cms_paths(self: "TestFilterByURLPatterns") -> None:
        """Test that CMS paths are excluded."""
        captures = [
            _capture("http://example.com/page"),
            _capture("http://example.com/wp-content/uploads/file.pdf"),
            _capture("http://example.com/wp-includes/js/jquery.js"),
        ]
        result = InternetArchiveCDXFilter.filter_by_url_patterns(
            captures, [r"/wp-content/", r"/wp-includes/"]
        )
        assert len(result) == 1

    def test_excludes_tracking_params(self: "TestFilterByURLPatterns") -> None:
        """Test that tracking parameter URLs are excluded."""
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
    """Tests for URL deduplication."""

    def test_keeps_latest_capture(self: "TestDeduplicateByURL") -> None:
        """Test that the latest capture is kept when deduplicating."""
        captures = [
            _capture("http://example.com/page", timestamp=20230101000000),
            _capture("http://example.com/page", timestamp=20240101000000),
        ]
        result = InternetArchiveCDXFilter.deduplicate_by_url(captures)
        assert len(result) == 1
        assert result[0].timestamp == 20240101000000

    def test_normalizes_trailing_slash(self: "TestDeduplicateByURL") -> None:
        """Test that trailing slashes are normalized."""
        captures = [
            _capture("http://example.com/page", timestamp=20230101000000),
            _capture("http://example.com/page/", timestamp=20240101000000),
        ]
        result = InternetArchiveCDXFilter.deduplicate_by_url(captures)
        assert len(result) == 1

    def test_normalizes_case(self: "TestDeduplicateByURL") -> None:
        """Test that domain case is normalized."""
        captures = [
            _capture("http://Example.COM/page", timestamp=20230101000000),
            _capture("http://example.com/page", timestamp=20240101000000),
        ]
        result = InternetArchiveCDXFilter.deduplicate_by_url(captures)
        assert len(result) == 1

    def test_normalizes_fragments_ignored(self: "TestDeduplicateByURL") -> None:
        """Test that URL fragments are ignored during deduplication."""
        captures = [
            _capture("http://example.com/page#section1"),
            _capture("http://example.com/page#section2"),
        ]
        result = InternetArchiveCDXFilter.deduplicate_by_url(captures)
        assert len(result) == 1

    def test_sorts_query_params(self: "TestDeduplicateByURL") -> None:
        """Test that query parameters are sorted for deduplication."""
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
    """Tests for the combined filter pipeline."""

    def test_end_to_end(self: "TestFilterAll") -> None:
        """Test that all filters are applied in sequence."""
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
