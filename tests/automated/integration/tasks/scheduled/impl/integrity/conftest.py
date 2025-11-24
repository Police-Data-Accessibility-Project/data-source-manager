import pytest

from src.core.tasks.scheduled.impl.integrity.operator import IntegrityMonitorTaskOperator
from src.db.client.async_ import AsyncDatabaseClient


@pytest.fixture
def operator(
    adb_client_test: AsyncDatabaseClient
) -> IntegrityMonitorTaskOperator:
    raise NotImplementedError