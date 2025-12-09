import pytest

from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.update.core import DSAppSyncMetaURLsUpdateTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.external.pdap.client import PDAPClient


@pytest.fixture
def operator(
    adb_client_test: AsyncDatabaseClient,
    mock_pdap_client: PDAPClient
) -> DSAppSyncMetaURLsUpdateTaskOperator:
    return DSAppSyncMetaURLsUpdateTaskOperator(
        adb_client=adb_client_test,
        pdap_client=mock_pdap_client
    )