"""Integration tests for the Internet Archive collector API endpoint."""
import time
from unittest import mock

from src.collectors.impl.internet_archive.dtos.input import InternetArchiveInputDTO
from src.collectors.impl.internet_archive.dtos.output import (
    InternetArchiveOutputDTO,
    InternetArchiveURLResult,
)
from tests.helpers.api_test_helper import APITestHelper

MOCK_PATH = (
    "src.collectors.impl.internet_archive.collector"
    ".InternetArchiveCrawler"
)


def _make_mock_crawler(results: list[InternetArchiveOutputDTO], messages: list[str] | None = None) -> mock.MagicMock:
    """Create a mock InternetArchiveCrawler class with the given results."""
    mock_cls = mock.MagicMock()
    mock_instance = mock.MagicMock()
    mock_instance.results = results

    async def mock_run() -> None:
        for msg in (messages or ["Crawling..."]):
            yield msg

    mock_instance.run = mock_run
    mock_cls.return_value = mock_instance
    return mock_cls


CANNED_RESULTS = [
    InternetArchiveOutputDTO(
        domain="example.gov",
        urls=[
            InternetArchiveURLResult(
                url="https://example.gov/page1",
                archive_url="https://web.archive.org/web/20240101000000/https://example.gov/page1",
                timestamp=20240101000000,
                digest="abc123",
            ),
            InternetArchiveURLResult(
                url="https://example.gov/page2",
                archive_url="https://web.archive.org/web/20240201000000/https://example.gov/page2",
                timestamp=20240201000000,
                digest="def456",
            ),
        ],
    )
]


def test_internet_archive_collector(api_test_helper: APITestHelper) -> None:
    """Test the Internet Archive collector API endpoint end-to-end."""
    ath = api_test_helper

    mock_cls = _make_mock_crawler(
        results=CANNED_RESULTS,
        messages=["Searching example.gov...", "Found 2 URLs"],
    )

    dto = InternetArchiveInputDTO(urls=["https://example.gov/police"])

    with mock.patch(MOCK_PATH, mock_cls):
        response = ath.request_validator.post(
            url="/collector/internet-archive",
            json=dto.model_dump(),
        )

        assert "batch_id" in response
        batch_id = response["batch_id"]

        # Give the background collector task time to complete
        time.sleep(1)

    batch_urls = ath.request_validator.get_batch_urls(batch_id)
    assert len(batch_urls.urls) == 2

    for url_info in batch_urls.urls:
        assert url_info.collector_metadata is not None
        assert "source_domain" in url_info.collector_metadata
        assert "archive_url" in url_info.collector_metadata
        assert "ia_timestamp" in url_info.collector_metadata
        assert "ia_digest" in url_info.collector_metadata


def test_internet_archive_collector_empty_domain(api_test_helper: APITestHelper) -> None:
    """Test the collector with a domain that returns no results."""
    ath = api_test_helper

    mock_cls = _make_mock_crawler(
        results=[
            InternetArchiveOutputDTO(domain="empty.gov", urls=[]),
        ],
        messages=["Searching empty.gov...", "Found 0 URLs"],
    )

    dto = InternetArchiveInputDTO(urls=["https://empty.gov/police"])

    with mock.patch(MOCK_PATH, mock_cls):
        response = ath.request_validator.post(
            url="/collector/internet-archive",
            json=dto.model_dump(),
        )

        batch_id = response["batch_id"]
        time.sleep(1)

    batch_urls = ath.request_validator.get_batch_urls(batch_id)
    assert len(batch_urls.urls) == 0


def test_internet_archive_collector_api_error(api_test_helper: APITestHelper) -> None:
    """Test the collector when the CDX API returns an error."""
    ath = api_test_helper

    mock_cls = _make_mock_crawler(
        results=[],
        messages=["Searching error.gov...", "Error: CDX API returned 503"],
    )

    dto = InternetArchiveInputDTO(urls=["https://error.gov/police"])

    with mock.patch(MOCK_PATH, mock_cls):
        response = ath.request_validator.post(
            url="/collector/internet-archive",
            json=dto.model_dump(),
        )

        batch_id = response["batch_id"]
        time.sleep(1)

    batch_urls = ath.request_validator.get_batch_urls(batch_id)
    assert len(batch_urls.urls) == 0
