import pytest

from src.collectors.enums import CollectorType, URLStatus
from src.core.enums import BatchStatus
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.mapping import URLMapping
from src.db.helpers.connect import get_postgres_connection_string
from src.db.models.impl.flag.url_validated.enums import URLValidatedType
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.data_creator.create import create_batch, create_url_data_sources, create_urls, \
    create_batch_url_links, create_validated_flags
from tests.helpers.setup.wipe import wipe_database


@pytest.mark.asyncio
async def test_get_batches_aggregated_metrics(
    api_test_helper,
    wiped_database
):
    ath = api_test_helper
    adb_client: AsyncDatabaseClient = ath.adb_client()
    # Create successful batches with URLs of different statuses
    for i in range(3):
        batch_id = await create_batch(
            adb_client=adb_client,
            strategy=CollectorType.MANUAL,
        )
        url_mappings_error: list[URLMapping] = await create_urls(
            adb_client=adb_client,
            status=URLStatus.ERROR,
            count=4,
        )
        url_mappings_ok: list[URLMapping] = await create_urls(
            adb_client=adb_client,
            status=URLStatus.OK,
            count=11,
        )
        url_mappings_all: list[URLMapping] = url_mappings_error + url_mappings_ok
        url_ids_all: list[int] = [url_mapping.url_id for url_mapping in url_mappings_all]
        await create_batch_url_links(
            adb_client=adb_client,
            batch_id=batch_id,
            url_ids=url_ids_all,
        )
        urls_submitted: list[int] = url_ids_all[:2]
        urls_not_relevant: list[int] = url_ids_all[2:5]
        urls_validated: list[int] = url_ids_all[5:10]
        await create_validated_flags(
            adb_client=adb_client,
            url_ids=urls_validated + urls_submitted,
            validation_type=URLValidatedType.DATA_SOURCE,
        )
        await create_validated_flags(
            adb_client=adb_client,
            url_ids=urls_not_relevant,
            validation_type=URLValidatedType.NOT_RELEVANT,
        )
        await create_url_data_sources(
            adb_client=adb_client,
            url_ids=urls_submitted,
        )

    all_params = []
    # Create failed batches
    for i in range(2):
        params = TestBatchCreationParameters(
            outcome=BatchStatus.ERROR
        )
        all_params.append(params)

    for params in all_params:
        await ath.db_data_creator.batch_v2(params)

    dto = await ath.request_validator.get_batches_aggregated_metrics()
    assert dto.total_batches == 5
    inner_dto_example = dto.by_strategy[CollectorType.EXAMPLE]
    assert inner_dto_example.count_urls == 0
    assert inner_dto_example.count_successful_batches == 0
    assert inner_dto_example.count_failed_batches == 2
    assert inner_dto_example.count_urls_pending == 0
    assert inner_dto_example.count_urls_submitted == 0
    assert inner_dto_example.count_urls_rejected == 0
    assert inner_dto_example.count_urls_errors == 0
    assert inner_dto_example.count_urls_validated == 0

    inner_dto_manual = dto.by_strategy[CollectorType.MANUAL]
    assert inner_dto_manual.count_urls == 45
    assert inner_dto_manual.count_successful_batches == 3
    assert inner_dto_manual.count_failed_batches == 0
    assert inner_dto_manual.count_urls_pending == 15
    assert inner_dto_manual.count_urls_submitted == 6
    assert inner_dto_manual.count_urls_rejected == 9
    assert inner_dto_manual.count_urls_errors == 12
    assert inner_dto_manual.count_urls_validated == 30
