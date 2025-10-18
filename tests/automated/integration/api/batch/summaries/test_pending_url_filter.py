import pytest

from src.collectors.enums import CollectorType
from src.core.enums import BatchStatus
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.db.models.views.batch_url_status.enums import BatchURLStatusEnum
from tests.helpers.batch_creation_parameters.enums import URLCreationEnum
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_get_batch_summaries_pending_url_filter(api_test_helper):
    ath = api_test_helper
    dbdc: DBDataCreator = ath.db_data_creator

    # Add an errored out batch
    batch_error: int = await dbdc.create_batch(status=BatchStatus.ERROR)

    # Add a batch with pending urls
    batch_pending = await ath.db_data_creator.batch_and_urls(
        strategy=CollectorType.EXAMPLE,
        url_count=2,
        batch_status=BatchStatus.READY_TO_LABEL,
        with_html_content=True,
        url_status=URLCreationEnum.OK
    )

    # Add a batch with submitted URLs
    batch_submitted: int = await dbdc.create_batch(status=BatchStatus.READY_TO_LABEL)
    submitted_url_mappings: list[SimpleURLMapping] = await dbdc.create_submitted_urls(count=2)
    submitted_url_ids: list[int] = [url_mapping.url_id for url_mapping in submitted_url_mappings]
    await dbdc.create_batch_url_links(
        batch_id=batch_submitted,
        url_ids=submitted_url_ids
    )

    # Add an aborted batch
    batch_aborted: int = await dbdc.create_batch(status=BatchStatus.ABORTED)

    # Add a batch with validated URLs
    batch_validated: int = await dbdc.create_batch(status=BatchStatus.READY_TO_LABEL)
    validated_url_mappings: list[SimpleURLMapping] = await dbdc.create_validated_urls(
        count=2
    )
    validated_url_ids: list[int] = [url_mapping.url_id for url_mapping in validated_url_mappings]
    await dbdc.create_batch_url_links(
        batch_id=batch_validated,
        url_ids=validated_url_ids
    )

    await dbdc.adb_client.refresh_materialized_views()

    # Test filter for pending URLs and only retrieve the second batch
    pending_urls_results = ath.request_validator.get_batch_statuses(
        status=BatchURLStatusEnum.HAS_UNLABELED_URLS
    )

    assert len(pending_urls_results.results) == 1
    assert pending_urls_results.results[0].id == batch_pending.batch_id
