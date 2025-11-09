import pytest

from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_validated_not_relevant(
    db_data_creator: DBDataCreator,
    api_test_helper: APITestHelper
):
    """
    Test that deletion works properly for a URL that is a validated
    as any of the non-relevant URL types
    (not relevant, broken, individual record)
    """

    url_ids: list[int] = await _setup(
        ddc=db_data_creator
    )
    for url_id in url_ids:
        api_test_helper.request_validator.delete_v3(
            f"url/{url_id}"
        )
    await _check_results(
        url_ids,
        dbc=db_data_creator.adb_client
    )



async def _check_results(
    url_ids: list[int],
    dbc: AsyncDatabaseClient
) -> None:
    pass
    # CHECK
    ## Each URLs Validation Flags should be deleted
    url_validation_flags: list[FlagURLValidated] = await dbc.get_all(FlagURLValidated)
    assert len(url_validation_flags) == 0

    ## Each URL should be deleted
    urls: list[URL] = await dbc.get_all(URL)
    assert len(urls) == 0

async def _setup(
    ddc: DBDataCreator
) -> list[int]:
    url_ids: list[int] = []
    # SETUP (3 URLs)
    for validated_type in [
        ## Validated Flag - Individual Record
        URLType.INDIVIDUAL_RECORD,
        ## Validated Flag - Broken
        URLType.BROKEN_PAGE,
        ## Validated Flag - Not Relevant
        URLType.NOT_RELEVANT
    ]:
        url_id: int = (await ddc.create_validated_urls(
            validation_type=validated_type,
            count=1
        ))[0].url_id
        url_ids.append(url_id)
    return url_ids



