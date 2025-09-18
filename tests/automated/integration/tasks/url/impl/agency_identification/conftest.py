from unittest.mock import create_autospec

import pytest

from src.collectors.impl.muckrock.api_interface.core import MuckrockAPIInterface
from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor import \
    NLPProcessor
from src.core.tasks.url.operators.agency_identification.subtasks.loader import AgencyIdentificationSubtaskLoader
from src.db.client.async_ import AsyncDatabaseClient
from src.external.pdap.client import PDAPClient


@pytest.fixture
def operator(
    adb_client_test: AsyncDatabaseClient
) -> AgencyIdentificationTaskOperator:

    operator = AgencyIdentificationTaskOperator(
        adb_client=adb_client_test,
        loader=AgencyIdentificationSubtaskLoader(
            pdap_client=create_autospec(PDAPClient),
            muckrock_api_interface=create_autospec(MuckrockAPIInterface),
            adb_client=adb_client_test,
            nlp_processor=create_autospec(NLPProcessor)
        ),
    )

    return operator
