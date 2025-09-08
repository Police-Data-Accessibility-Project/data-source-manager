import pytest

from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_nlp_location_match(
    db_data_creator: DBDataCreator,
    operator: AgencyIdentificationTaskOperator
):

    # Create 2 URLs with compressed HTML
    url_mappings: list[URLMapping] = await db_data_creator.create_urls(count=2)
    url_ids: list[int] = [url.url_id for url in url_mappings]
    await db_data_creator.html_data(url_ids=url_ids)

    # Confirm operator meets prerequisites
    assert await operator.meets_task_prerequisites()
    assert operator._subtask == AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH

    # raise NotImplementedError