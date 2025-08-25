from datetime import datetime, timedelta

import pendulum
import pytest

from src.collectors.enums import CollectorType, URLStatus
from src.core.enums import BatchStatus
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.url_validated.enums import ValidatedURLType
from tests.helpers.data_creator.create import create_batch, create_urls, create_batch_url_links, create_validated_flags, \
    create_url_data_sources


@pytest.mark.asyncio
async def test_get_batches_breakdown_metrics(api_test_helper):
    # Create a different batch for each month, with different URLs
    today = datetime.now()
    ath = api_test_helper
    adb_client: AsyncDatabaseClient = ath.adb_client()

    batch_id_1 = await create_batch(
        adb_client=adb_client,
        strategy=CollectorType.MANUAL,
    )
    url_ids_1: list[int] = await create_urls(
        adb_client=adb_client,
        count=3,
    )
    await create_batch_url_links(adb_client=adb_client, batch_id=batch_id_1, url_ids=url_ids_1)
    await create_validated_flags(
        adb_client=adb_client,
        url_ids=url_ids_1[:2],
        validation_type=ValidatedURLType.DATA_SOURCE
    )
    await create_url_data_sources(
        adb_client=adb_client,
        url_ids=url_ids_1[:2],
    )

    batch_id_2 = await create_batch(
        adb_client=adb_client,
        status=BatchStatus.ERROR,
        date_generated=today - timedelta(days=7),
    )

    batch_id_3 = await create_batch(
        adb_client=adb_client,
        strategy=CollectorType.AUTO_GOOGLER,
        date_generated=today - timedelta(days=14)
    )
    error_url_ids: list[int] = await create_urls(
        adb_client=adb_client,
        status=URLStatus.ERROR,
        count=4,
    )
    validated_url_ids: list[int] = await create_urls(
        adb_client=adb_client,
        count=8,
    )
    await create_validated_flags(
        adb_client=adb_client,
        url_ids=validated_url_ids[:3],
        validation_type=ValidatedURLType.NOT_RELEVANT,
    )
    await create_validated_flags(
        adb_client=adb_client,
        url_ids=validated_url_ids[4:9],
        validation_type=ValidatedURLType.DATA_SOURCE,
    )
    await create_batch_url_links(
        adb_client=adb_client,
        batch_id=batch_id_3,
        url_ids=error_url_ids + validated_url_ids,
    )


    dto_1 = await ath.request_validator.get_batches_breakdown_metrics(
        page=1
    )
    assert len(dto_1.batches) == 3
    dto_batch_1 = dto_1.batches[2]
    assert dto_batch_1.batch_id == batch_id_1
    assert dto_batch_1.strategy == CollectorType.MANUAL
    assert dto_batch_1.status == BatchStatus.READY_TO_LABEL
    assert dto_batch_1.count_url_total == 3
    assert dto_batch_1.count_url_pending == 1
    assert dto_batch_1.count_url_submitted == 2
    assert dto_batch_1.count_url_rejected == 0
    assert dto_batch_1.count_url_error == 0
    assert dto_batch_1.count_url_validated == 2

    dto_batch_2 = dto_1.batches[1]
    assert dto_batch_2.batch_id == batch_id_2
    assert dto_batch_2.status == BatchStatus.ERROR
    assert dto_batch_2.strategy == CollectorType.EXAMPLE
    assert dto_batch_2.count_url_total == 0
    assert dto_batch_2.count_url_submitted == 0
    assert dto_batch_2.count_url_pending == 0
    assert dto_batch_2.count_url_rejected == 0
    assert dto_batch_2.count_url_error == 0
    assert dto_batch_2.count_url_validated == 0

    dto_batch_3 = dto_1.batches[0]
    assert dto_batch_3.batch_id == batch_id_3
    assert dto_batch_3.status == BatchStatus.READY_TO_LABEL
    assert dto_batch_3.strategy == CollectorType.AUTO_GOOGLER
    assert dto_batch_3.count_url_total == 12
    assert dto_batch_3.count_url_pending == 5
    assert dto_batch_3.count_url_submitted == 0
    assert dto_batch_3.count_url_rejected == 3
    assert dto_batch_3.count_url_error == 4
    assert dto_batch_3.count_url_validated == 7

    dto_2 = await ath.request_validator.get_batches_breakdown_metrics(
        page=2
    )
    assert len(dto_2.batches) == 0
