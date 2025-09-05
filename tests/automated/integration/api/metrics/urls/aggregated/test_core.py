from datetime import datetime, timedelta, timezone

import pendulum
import pytest

from src.collectors.enums import CollectorType, URLStatus
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.flag.url_validated.enums import URLValidatedType
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.enums import URLCreationEnum
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_get_urls_aggregated_metrics(api_test_helper):
    ath = api_test_helper
    today = datetime.now()

    ddc: DBDataCreator = ath.db_data_creator

    batch_0_params = TestBatchCreationParameters(
        strategy=CollectorType.MANUAL,
        created_at=today - timedelta(days=1),
        urls=[
            TestURLCreationParameters(
                count=1,
                status=URLCreationEnum.OK,
            ),
        ]
    )
    batch_0: int = await ddc.create_batch(
        strategy=CollectorType.MANUAL,
        date_generated=today - timedelta(days=1)
    )
    url_mappings_0: list[URLMapping] = await ddc.create_urls(batch_id=batch_0)
    oldest_url_id: int = url_mappings_0[0].url_id

    batch_1: int = await ddc.create_batch(
        strategy=CollectorType.MANUAL,
    )
    url_mappings_1_ok: list[URLMapping] = await ddc.create_urls(batch_id=batch_1, count=1)
    url_mappings_1_submitted: list[URLMapping] = await ddc.create_submitted_urls(count=2)
    url_ids_1_submitted: list[int] = [url_mapping.url_id for url_mapping in url_mappings_1_submitted]
    await ddc.create_batch_url_links(url_ids=url_ids_1_submitted, batch_id=batch_1)

    batch_2: int = await ddc.create_batch(
        strategy=CollectorType.AUTO_GOOGLER,
    )
    url_mappings_2_ok: list[URLMapping] = await ddc.create_urls(batch_id=batch_2, count=4, status=URLStatus.OK)
    url_mappings_2_error: list[URLMapping] = await ddc.create_urls(batch_id=batch_2, count=2, status=URLStatus.ERROR)
    url_mappings_2_validated: list[URLMapping] = await ddc.create_validated_urls(count=1, validation_type=URLValidatedType.DATA_SOURCE)
    url_mappings_2_not_relevant: list[URLMapping] = await ddc.create_validated_urls(count=5, validation_type=URLValidatedType.NOT_RELEVANT)
    url_ids_2_validated: list[int] = [url_mapping.url_id for url_mapping in url_mappings_2_validated]
    url_ids_2_not_relevant: list[int] = [url_mapping.url_id for url_mapping in url_mappings_2_not_relevant]
    await ddc.create_batch_url_links(
        url_ids=url_ids_2_validated + url_ids_2_not_relevant,
        batch_id=batch_2
    )



    dto = await ath.request_validator.get_urls_aggregated_metrics()

    assert dto.oldest_pending_url_id == oldest_url_id
    assert dto.count_urls_rejected == 5
    assert dto.count_urls_errors == 2
    assert dto.count_urls_validated == 8
    assert dto.count_urls_submitted == 2
    assert dto.count_urls_total == 16
