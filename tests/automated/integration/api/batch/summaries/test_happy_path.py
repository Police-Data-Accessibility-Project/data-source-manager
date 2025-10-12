import pytest

from src.core.enums import BatchStatus
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.enums import URLCreationEnum
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters


@pytest.mark.asyncio
async def test_get_batch_summaries(api_test_helper):
    ath = api_test_helper

    batch_params = [
        TestBatchCreationParameters(
            urls=[
                TestURLCreationParameters(
                    count=1,
                    status=URLCreationEnum.OK
                ),
                TestURLCreationParameters(
                    count=2,
                    status=URLCreationEnum.SUBMITTED
                )
            ]
        ),
        TestBatchCreationParameters(
            urls=[
                TestURLCreationParameters(
                    count=4,
                    status=URLCreationEnum.NOT_RELEVANT
                ),
                TestURLCreationParameters(
                    count=3,
                    status=URLCreationEnum.ERROR
                )
            ]
        ),
        TestBatchCreationParameters(
            urls=[
                TestURLCreationParameters(
                    count=7,
                    status=URLCreationEnum.DUPLICATE
                ),
                TestURLCreationParameters(
                    count=1,
                    status=URLCreationEnum.SUBMITTED
                )
            ]
        )
    ]

    batch_1_creation_info = await ath.db_data_creator.batch_v2(batch_params[0])
    batch_2_creation_info = await ath.db_data_creator.batch_v2(batch_params[1])
    batch_3_creation_info = await ath.db_data_creator.batch_v2(batch_params[2])

    batch_1_id = batch_1_creation_info.batch_id
    batch_2_id = batch_2_creation_info.batch_id
    batch_3_id = batch_3_creation_info.batch_id

    await ath.adb_client().refresh_materialized_views()

    response = ath.request_validator.get_batch_statuses()
    results = response.results

    assert len(results) == 3

    result_1 = results[0]
    assert result_1.id == batch_1_id
    assert result_1.status == BatchStatus.READY_TO_LABEL
    counts_1 = result_1.url_counts
    assert counts_1.total == 3
    assert counts_1.pending == 1
    assert counts_1.submitted == 2
    assert counts_1.not_relevant == 0
    assert counts_1.duplicate == 0
    assert counts_1.errored == 0

    result_2 = results[1]
    assert result_2.id == batch_2_id
    counts_2 = result_2.url_counts
    assert counts_2.total == 7
    assert counts_2.not_relevant == 4
    assert counts_2.errored == 3
    assert counts_2.pending == 3
    assert counts_2.submitted == 0
    assert counts_2.duplicate == 0

    result_3 = results[2]
    assert result_3.id == batch_3_id
    counts_3 = result_3.url_counts
    assert counts_3.total == 8
    assert counts_3.not_relevant == 0
    assert counts_3.errored == 0
    assert counts_3.pending == 7
    assert counts_3.submitted == 1
    assert counts_3.duplicate == 7
