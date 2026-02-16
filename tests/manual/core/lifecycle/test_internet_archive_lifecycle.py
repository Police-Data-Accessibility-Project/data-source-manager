"""Manual lifecycle test for the Internet Archive collector."""
import asyncio
from unittest.mock import MagicMock

import pytest

from src.collectors.enums import CollectorType
from src.collectors.impl.internet_archive.dtos.input import InternetArchiveInputDTO
from src.collectors.manager import AsyncCollectorManager
from src.core.core import AsyncCore
from src.core.enums import BatchStatus
from src.core.logger import AsyncCoreLogger
from src.db.client.async_ import AsyncDatabaseClient


@pytest.fixture
def manual_async_core(adb_client_test: AsyncDatabaseClient) -> AsyncCore:
    """Create an AsyncCore instance for manual testing."""
    logger = AsyncCoreLogger(adb_client=adb_client_test)
    adb_client = AsyncDatabaseClient()
    core = AsyncCore(
        adb_client=adb_client,
        task_manager=MagicMock(),
        collector_manager=AsyncCollectorManager(
            adb_client=adb_client,
            logger=logger,
            dev_mode=True,
        ),
    )
    yield core


@pytest.mark.manual
@pytest.mark.asyncio
async def test_internet_archive_lifecycle(manual_async_core: AsyncCore) -> None:
    """Test the full Internet Archive collector lifecycle against live APIs."""
    core = manual_async_core

    dto = InternetArchiveInputDTO(
        urls=["https://www.townofmorrisville.org/government/departments-services/police"],
        max_results_per_domain=100,
    )

    start_info = await core.initiate_collector(
        collector_type=CollectorType.INTERNET_ARCHIVE,
        dto=dto,
        user_id=1,
    )
    batch_id = start_info.batch_id

    # Await the background collector task directly
    task = core.collector_manager.async_tasks[batch_id]
    await asyncio.wait_for(task, timeout=60)

    # Verify the collector completed and inserted URLs
    collector = core.collector_manager.collectors[batch_id]
    assert collector.status == BatchStatus.READY_TO_LABEL

    batch_urls = await core.adb_client.get_urls_by_batch(batch_id)
    assert len(batch_urls) > 0

    first_url = batch_urls[0]
    assert first_url.collector_metadata is not None
    assert "source_domain" in first_url.collector_metadata
    assert "archive_url" in first_url.collector_metadata
    assert "ia_timestamp" in first_url.collector_metadata
    assert "ia_digest" in first_url.collector_metadata
