from unittest.mock import AsyncMock

import pytest_asyncio

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.core import \
    AgencyIDSubtaskInternalProcessor
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.core import \
    NLPProcessor
from src.external.pdap.client import PDAPClient


@pytest_asyncio.fixture
async def internal_processor() -> AgencyIDSubtaskInternalProcessor:
    return AgencyIDSubtaskInternalProcessor(
        nlp_processor=AsyncMock(spec=NLPProcessor),
        pdap_client=AsyncMock(spec=PDAPClient),
        task_id=1
    )