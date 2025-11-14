import pytest

from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.update.core import DSAppSyncAgenciesUpdateTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.external.pdap.client import PDAPClient


@pytest.fixture
def operator(
    adb_client_test: AsyncDatabaseClient,
    mock_pdap_client: PDAPClient
) -> DSAppSyncAgenciesUpdateTaskOperator:
    return DSAppSyncAgenciesUpdateTaskOperator(
        adb_client=adb_client_test,
        pdap_client=mock_pdap_client
    )