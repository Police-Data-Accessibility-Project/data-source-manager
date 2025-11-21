import pendulum
import pytest

from src.collectors.enums import URLStatus
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_get_backlog_metrics(api_test_helper):
    today = pendulum.parse('2021-01-01')

    ath = api_test_helper
    adb_client = ath.adb_client()
    ddc: DBDataCreator = ath.db_data_creator


    # Populate the backlog table and test that backlog metrics returned on a monthly basis
    # Ensure that multiple days in each month are added to the backlog table, with different values

    batch_1_id: int = await ddc.create_batch()
    url_mappings_1: list[SimpleURLMapping] = await ddc.create_urls(count=3)
    url_ids_1: list[int] = [url_mapping.url_id for url_mapping in url_mappings_1]
    await ddc.create_batch_url_links(url_ids=url_ids_1, batch_id=batch_1_id)
    submitted_url_ids_1: list[int] = url_ids_1[:2]
    await ddc.create_validated_flags(
        url_ids=submitted_url_ids_1,
        validation_type=URLType.DATA_SOURCE
    )
    await ddc.create_url_data_sources(url_ids=submitted_url_ids_1)

    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=3).naive()
    )

    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=2, days=3).naive()
    )

    batch_2_id: int = await ddc.create_batch()
    not_relevant_url_mappings_2: list[SimpleURLMapping] = await ddc.create_urls(count=6)
    not_relevant_url_ids_2: list[int] = [url_mapping.url_id for url_mapping in not_relevant_url_mappings_2]
    await ddc.create_batch_url_links(url_ids=not_relevant_url_ids_2, batch_id=batch_2_id)
    await ddc.create_validated_flags(
        url_ids=not_relevant_url_ids_2[:4],
        validation_type=URLType.NOT_RELEVANT
    )

    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=2).naive()
    )

    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=1, days=4).naive()
    )

    batch_3_id: int = await ddc.create_batch()
    url_mappings_3: list[SimpleURLMapping] = await ddc.create_urls(count=12)
    url_ids_3: list[int] = [url_mapping.url_id for url_mapping in url_mappings_3]
    await ddc.create_batch_url_links(url_ids=url_ids_3, batch_id=batch_3_id)
    await ddc.create_validated_flags(
        url_ids=url_ids_3[:5],
        validation_type=URLType.DATA_SOURCE
    )


    await adb_client.populate_backlog_snapshot(
        dt=today.subtract(months=1).naive()
    )

    dto = await ath.request_validator.get_backlog_metrics()

    assert len(dto.entries) == 3

    # Test that the count closest to the beginning of the month is returned for each month
    assert dto.entries[0].count_pending_total == 1
    assert dto.entries[1].count_pending_total == 3
    assert dto.entries[2].count_pending_total == 10
