import pytest

from src.collectors.enums import URLStatus
from src.db.dtos.url.mapping import URLMapping
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.batch.v1 import BatchURLCreationInfo


@pytest.mark.asyncio
async def test_batch_filtering(
    batch_url_creation_info: BatchURLCreationInfo,
    api_test_helper
):
    ath = api_test_helper
    rv = ath.request_validator

    dbdc: DBDataCreator = ath.db_data_creator

    batch_id: int = batch_url_creation_info.batch_id

    validated_url_mappings: list[URLMapping] = await dbdc.create_validated_urls(count=4)
    validated_url_ids: list[int] = [url_mapping.url_id for url_mapping in validated_url_mappings]
    await dbdc.create_batch_url_links(
        url_ids=validated_url_ids,
        batch_id=batch_id
    )

    # Receive null batch info if batch id not provided
    outer_result_no_batch_info = await rv.review_next_source()
    assert outer_result_no_batch_info.next_source.batch_info is None

    # Get batch info if batch id is provided
    outer_result = await ath.request_validator.review_next_source(
        batch_id=batch_id
    )
    assert outer_result.remaining == 2
    batch_info = outer_result.next_source.batch_info
    assert batch_info.count_reviewed == 4
    assert batch_info.count_ready_for_review == 2

