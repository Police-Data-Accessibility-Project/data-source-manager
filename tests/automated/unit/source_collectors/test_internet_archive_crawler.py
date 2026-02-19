"""Tests for the Internet Archive crawler."""
from unittest import mock

import pytest

from src.collectors.impl.internet_archive.crawler import InternetArchiveCrawler
from src.external.internet_archives.models.capture import IACapture
from src.external.internet_archives.models.domain_search import IADomainSearchResult


def _make_capture(
    url: str,
    timestamp: int = 20240101000000,
    mimetype: str = "text/html",
) -> IACapture:
    """Create an IACapture for testing."""
    return IACapture(
        original=url,
        timestamp=timestamp,
        length=1000,
        digest="abc123",
        mimetype=mimetype,
    )


@pytest.fixture
def mock_search_domain_urls() -> mock.MagicMock:
    """Patch InternetArchivesClient.search_domain_urls."""
    mock_path = (
        "src.collectors.impl.internet_archive.crawler"
        ".InternetArchivesClient.search_domain_urls"
    )
    with mock.patch(mock_path) as mock_fn:
        yield mock_fn


@pytest.fixture
def mock_env() -> mock.MagicMock:
    """Patch the Env class used by InternetArchivesClient."""
    mock_path = (
        "src.external.internet_archives.client.Env"
    )
    with mock.patch(mock_path) as mock_env_cls:
        mock_env_instance = mock.MagicMock()
        mock_env_instance.str.return_value = "fake_s3_keys"
        mock_env_cls.return_value = mock_env_instance
        yield mock_env_cls


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_env")
async def test_domain_extraction(mock_search_domain_urls: mock.MagicMock) -> None:
    """Test that domains are correctly extracted from seed URLs."""
    mock_search_domain_urls.return_value = IADomainSearchResult(
        domain="example.gov", captures=[]
    )
    crawler = InternetArchiveCrawler(
        urls=["https://example.gov/police-data", "http://example.gov/reports"]
    )
    async for _ in crawler.run():
        pass
    mock_search_domain_urls.assert_called_once_with(
        domain="example.gov", limit=10000
    )


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_env")
async def test_multiple_domains(mock_search_domain_urls: mock.MagicMock) -> None:
    """Test that multiple domains are searched independently."""
    mock_search_domain_urls.return_value = IADomainSearchResult(
        domain="test.gov", captures=[]
    )
    crawler = InternetArchiveCrawler(
        urls=[
            "https://alpha.gov/page",
            "https://beta.gov/page",
        ]
    )
    async for _ in crawler.run():
        pass
    assert mock_search_domain_urls.call_count == 2


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_env")
async def test_seed_url_exclusion(mock_search_domain_urls: mock.MagicMock) -> None:
    """Test that seed URLs are excluded from results."""
    seed = "https://example.gov/police-data"
    mock_search_domain_urls.return_value = IADomainSearchResult(
        domain="example.gov",
        captures=[
            _make_capture("https://example.gov/police-data"),
            _make_capture("https://example.gov/other-page"),
        ],
    )
    crawler = InternetArchiveCrawler(urls=[seed])
    async for _ in crawler.run():
        pass
    assert len(crawler.results) == 1
    result_urls = [u.url for u in crawler.results[0].urls]
    assert seed not in result_urls
    assert "https://example.gov/other-page" in result_urls


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_env")
async def test_filtering_applied(mock_search_domain_urls: mock.MagicMock) -> None:
    """Test that MIME type filtering is applied."""
    mock_search_domain_urls.return_value = IADomainSearchResult(
        domain="example.gov",
        captures=[
            _make_capture("https://example.gov/page", mimetype="text/html"),
            _make_capture("https://example.gov/style.css", mimetype="text/css"),
        ],
    )
    crawler = InternetArchiveCrawler(
        urls=["https://example.gov/seed"],
        mime_type_allowlist=["text/html"],
    )
    async for _ in crawler.run():
        pass
    assert len(crawler.results[0].urls) == 1
    assert crawler.results[0].urls[0].url == "https://example.gov/page"


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_env")
async def test_error_handling_continues(mock_search_domain_urls: mock.MagicMock) -> None:
    """Test that errors on one domain do not stop other domains."""
    async def side_effect(domain: str, limit: int) -> IADomainSearchResult:  # noqa: U100
        if domain == "broken.gov":
            return IADomainSearchResult(
                domain=domain, captures=[], error="ConnectionError: timeout"
            )
        return IADomainSearchResult(
            domain=domain,
            captures=[_make_capture(f"https://{domain}/page")],
        )

    mock_search_domain_urls.side_effect = side_effect
    crawler = InternetArchiveCrawler(
        urls=["https://broken.gov/seed", "https://working.gov/seed"]
    )
    messages = []
    async for msg in crawler.run():
        messages.append(msg)

    assert any("Error" in m for m in messages)
    assert len(crawler.results) == 1
    assert crawler.results[0].domain == "working.gov"


@pytest.mark.asyncio
@pytest.mark.usefixtures("mock_env")
async def test_archive_url_format(mock_search_domain_urls: mock.MagicMock) -> None:
    """Test that archive URLs are correctly formatted."""
    mock_search_domain_urls.return_value = IADomainSearchResult(
        domain="example.gov",
        captures=[
            _make_capture(
                "https://example.gov/page", timestamp=20240315120000
            ),
        ],
    )
    crawler = InternetArchiveCrawler(urls=["https://example.gov/seed"])
    async for _ in crawler.run():
        pass
    url_result = crawler.results[0].urls[0]
    assert url_result.archive_url == (
        "https://web.archive.org/web/20240315120000/"
        "https://example.gov/page"
    )
