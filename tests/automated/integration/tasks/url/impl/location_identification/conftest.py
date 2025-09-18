from unittest.mock import create_autospec

import pytest

from src.core.tasks.url.operators.location_id.core import LocationIdentificationTaskOperator
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.nlp.core import NLPProcessor
from src.core.tasks.url.operators.location_id.subtasks.loader import LocationIdentificationSubtaskLoader
from src.db.client.async_ import AsyncDatabaseClient


@pytest.fixture
def operator(
    adb_client_test: AsyncDatabaseClient
) -> LocationIdentificationTaskOperator:

    operator = LocationIdentificationTaskOperator(
        adb_client=adb_client_test,
        loader=LocationIdentificationSubtaskLoader(
            adb_client=adb_client_test,
            nlp_processor=create_autospec(NLPProcessor)
        )
    )
    return operator