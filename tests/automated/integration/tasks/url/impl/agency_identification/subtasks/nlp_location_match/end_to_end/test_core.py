from unittest.mock import AsyncMock

import pytest

from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.core import \
    AgencyIDSubtaskInternalProcessor
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType

PATCH_ROOT = (
    "src.core.tasks.url.operators.agency_identification.subtasks." +
    "impl.nlp_location_match_.core.AgencyIDSubtaskInternalProcessor"
)

@pytest.mark.asyncio
async def test_nlp_location_match(
    operator: AgencyIdentificationTaskOperator,
    url_ids: list[int],
    monkeypatch
):
    # Confirm operator meets prerequisites
    assert await operator.meets_task_prerequisites()
    assert operator._subtask == AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH

    mock_internal_processor = AsyncMock(spec=AgencyIDSubtaskInternalProcessor)
    monkeypatch.setattr(PATCH_ROOT, mock_internal_processor)

#
    raise NotImplementedError