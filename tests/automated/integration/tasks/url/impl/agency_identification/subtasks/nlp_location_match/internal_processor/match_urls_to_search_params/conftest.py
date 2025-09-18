from unittest.mock import AsyncMock

import pytest

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.core import \
    AgencyIDSubtaskInternalProcessor
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor import \
    NLPProcessor
from src.external.pdap.client import PDAPClient


@pytest.fixture
def internal_processor() -> AgencyIDSubtaskInternalProcessor:
    return AgencyIDSubtaskInternalProcessor(
        nlp_processor=AsyncMock(spec=NLPProcessor),
        pdap_client=AsyncMock(PDAPClient),
        task_id=1
    )
