"""Tests for the Internet Archive collector."""
from unittest import mock

import pytest

from src.collectors.impl.internet_archive.collector import InternetArchiveCollector
from src.collectors.impl.internet_archive.dtos.input import InternetArchiveInputDTO
from src.collectors.impl.internet_archive.dtos.output import (
    InternetArchiveOutputDTO,
    InternetArchiveURLResult,
)
from src.core.logger import AsyncCoreLogger
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.info import URLInfo


@pytest.fixture
def mock_crawler() -> mock.MagicMock:
    """Create a mock InternetArchiveCrawler with canned results."""
    mock_path = (
        "src.collectors.impl.internet_archive.collector"
        ".InternetArchiveCrawler"
    )
    with mock.patch(mock_path) as mock_cls:
        mock_instance = mock.MagicMock()
        mock_instance.results = [
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

        async def mock_run() -> None:
            yield "Searching example.gov..."
            yield "Found 2 URLs"

        mock_instance.run = mock_run
        mock_cls.return_value = mock_instance
        yield mock_cls


@pytest.mark.asyncio
async def test_internet_archive_collector(mock_crawler: mock.MagicMock) -> None:
    """Test that the collector runs the crawler and preprocesses results."""
    collector = InternetArchiveCollector(
        batch_id=1,
        dto=InternetArchiveInputDTO(
            urls=["https://example.gov/seed"],
        ),
        logger=mock.AsyncMock(spec=AsyncCoreLogger),
        adb_client=mock.AsyncMock(spec=AsyncDatabaseClient),
        raise_error=True,
    )
    await collector.run()

    mock_crawler.assert_called_once()

    collector.adb_client.insert_urls.assert_called_once_with(
        url_infos=[
            URLInfo(
                url="https://example.gov/page1",
                collector_metadata={
                    "source_domain": "example.gov",
                    "archive_url": "https://web.archive.org/web/20240101000000/https://example.gov/page1",
                    "ia_timestamp": 20240101000000,
                    "ia_digest": "abc123",
                },
                source=URLSource.COLLECTOR,
            ),
            URLInfo(
                url="https://example.gov/page2",
                collector_metadata={
                    "source_domain": "example.gov",
                    "archive_url": "https://web.archive.org/web/20240201000000/https://example.gov/page2",
                    "ia_timestamp": 20240201000000,
                    "ia_digest": "def456",
                },
                source=URLSource.COLLECTOR,
            ),
        ],
        batch_id=1,
    )
