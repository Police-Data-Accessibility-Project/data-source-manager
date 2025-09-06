import pytest

from src.collectors.enums import URLStatus
from tests.helpers.batch_creation_parameters.enums import URLCreationEnum
from tests.helpers.setup.annotation.core import setup_for_get_next_url_for_annotation
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_get_next_url_for_user_relevance_annotation_validated(
        db_data_creator: DBDataCreator
):
    """
    A validated URL should not turn up in get_next_url_for_user_annotation
    """
    dbdc = db_data_creator
    url_1: int = (await dbdc.create_validated_urls())[0].url_id

    # Add `Relevancy` attribute with value `True`
    await db_data_creator.auto_relevant_suggestions(
        url_id=url_1,
        relevant=True
    )

    adb_client = db_data_creator.adb_client
    url = await adb_client.get_next_url_for_relevance_annotation(
        user_id=1,
        batch_id=None
    )
    assert url is None
