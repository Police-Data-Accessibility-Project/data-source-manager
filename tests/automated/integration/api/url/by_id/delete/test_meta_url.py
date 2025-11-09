import pytest

from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.ds_delete.meta_url import FlagDSDeleteMetaURL
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_meta_url(
    db_data_creator: DBDataCreator,
    api_test_helper: APITestHelper,
    test_agency_id: int
):
    """
    Test that deletion works properly for a URL that is a validated meta url
    and has all data source-only attributes.
    """

    url_id: int = await _setup(
        ddc=db_data_creator,
        agency_id=test_agency_id
    )
    api_test_helper.request_validator.delete_v3(
        f"url/{url_id}"
    )
    await _check_results(
        dbc=db_data_creator.adb_client
    )


async def _check_results(
    dbc: AsyncDatabaseClient
) -> None:
    pass
    # CHECK
    ## URL and all associated tables should be deleted
    assert await dbc.has_no_rows(URL)

    ## DS App Link should not yet be deleted
    app_link: DSAppLinkMetaURL = await dbc.one_or_none_model(DSAppLinkMetaURL)
    assert app_link is not None

    ## DS App Meta URL Deletion Flag should be added
    flag: FlagDSDeleteMetaURL = await dbc.one_or_none_model(FlagDSDeleteMetaURL)
    assert flag is not None
    assert flag.ds_meta_url_id == app_link.ds_meta_url_id


async def _setup(
    ddc: DBDataCreator,
    agency_id: int
) -> int:
    pass
    # SETUP
    ## Validated Flag - Meta URL
    url_id: int = (await ddc.create_validated_urls(
        validation_type=URLType.META_URL,
        count=1
    ))[0].url_id

    ## Link Agency
    await ddc.create_url_agency_links(
        url_ids=[url_id],
        agency_ids=[agency_id]
    )
    ## DS App Link
    app_link = DSAppLinkMetaURL(
        url_id=url_id,
        agency_id=agency_id,
        ds_meta_url_id=1
    )
    await ddc.adb_client.add(app_link)
    return url_id

