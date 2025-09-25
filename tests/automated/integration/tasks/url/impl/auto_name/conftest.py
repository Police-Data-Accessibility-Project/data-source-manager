import pytest

from src.core.tasks.url.operators.auto_name.core import AutoNameURLTaskOperator
from src.db.client.async_ import AsyncDatabaseClient


@pytest.fixture
def operator(
    adb_client_test: AsyncDatabaseClient
) -> AutoNameURLTaskOperator:
    operator = AutoNameURLTaskOperator(
        adb_client=adb_client_test,
    )
    return operator