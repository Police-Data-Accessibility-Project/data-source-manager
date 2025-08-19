from unittest.mock import AsyncMock

import pytest
from aiohttp import ClientSession

from src.core.tasks.scheduled.impl.internet_archives.save.operator import InternetArchivesSaveTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.external.internet_archives.client import InternetArchivesClient


@pytest.fixture
def operator(
    adb_client_test: AsyncDatabaseClient
) -> InternetArchivesSaveTaskOperator:
    return InternetArchivesSaveTaskOperator(
        adb_client=adb_client_test,
        ia_client=InternetArchivesClient(
            session=AsyncMock(spec=ClientSession)
        )
    )