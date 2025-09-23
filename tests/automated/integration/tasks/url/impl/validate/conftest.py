import pytest

from src.core.tasks.url.operators.validate.core import AutoValidateURLTaskOperator
from src.db.client.async_ import AsyncDatabaseClient


@pytest.fixture
def operator(
    adb_client_test: AsyncDatabaseClient
) -> AutoValidateURLTaskOperator:
    return AutoValidateURLTaskOperator(
        adb_client=adb_client_test,
    )