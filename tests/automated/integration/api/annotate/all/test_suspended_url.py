import pytest

from src.db.models.impl.flag.url_suspended.sqlalchemy import FlagURLSuspended
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review


@pytest.mark.asyncio
async def test_annotate_all(
    api_test_helper,
):
    """
    Test that a suspended URL is not returned for annotation.
    """
    ath = api_test_helper
    setup_info_1 = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator, include_user_annotations=True
    )

    get_response_1 = await ath.request_validator.get_next_url_for_all_annotations()
    assert get_response_1.next_annotation is not None

    adb_client = ath.adb_client()
    await adb_client.add(
        FlagURLSuspended(
            url_id=setup_info_1.url_mapping.url_id,
        )
    )
    get_response_2 = await ath.request_validator.get_next_url_for_all_annotations()
    assert get_response_2.next_annotation is None