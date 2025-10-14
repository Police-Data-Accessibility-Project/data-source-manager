from unittest.mock import create_autospec, AsyncMock

import pytest

from src.core.tasks.scheduled.impl.internet_archives.probe.operator import InternetArchivesProbeTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.external.internet_archives.client import InternetArchivesClient


@pytest.fixture
def operator(adb_client_test: AsyncDatabaseClient) -> InternetArchivesProbeTaskOperator:
    ia_client = InternetArchivesClient(
        session=AsyncMock()
    )
    ia_client._get_url_snapshot = create_autospec(
        ia_client._get_url_snapshot,
    )

    return InternetArchivesProbeTaskOperator(
        adb_client=adb_client_test,
        ia_client=ia_client
    )