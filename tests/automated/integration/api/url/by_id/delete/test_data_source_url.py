from datetime import date

import pytest

from src.core.enums import RecordType
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.ds_delete.data_source import FlagDSDeleteDataSource
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from src.db.models.impl.url.optional_ds_metadata.enums import AccessTypeEnum, RetentionScheduleEnum, UpdateMethodEnum, \
    AgencyAggregationEnum
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_data_source_url(
    db_data_creator: DBDataCreator,
    api_test_helper: APITestHelper,
    test_agency_id: int
):
    """
    Test that deletion works properly for a URL that is a validated data source
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

    ### Record Type should be deleted
    assert await dbc.has_no_rows(URLOptionalDataSourceMetadata)
    assert await dbc.has_no_rows(LinkURLAgency)
    assert await dbc.has_no_rows(URLRecordType)

    ## DS App Link should not yet be deleted
    app_link: DSAppLinkDataSource = await dbc.one_or_none_model(DSAppLinkDataSource)
    assert app_link is not None

    ## DS App Data Source Deletion Flag should be added
    flag: FlagDSDeleteDataSource = await dbc.one_or_none_model(FlagDSDeleteDataSource)
    assert flag is not None
    assert flag.ds_data_source_id == app_link.ds_data_source_id


async def _setup(
    ddc: DBDataCreator,
    agency_id: int
) -> int:
    pass
    # SETUP
    ## Validated Flag - Data Source
    ## Record Type
    url_id: int = (await ddc.create_validated_urls(
        validation_type=URLType.DATA_SOURCE,
        record_type=RecordType.BOOKING_REPORTS,
        count=1
    ))[0].url_id

    ## Link Agency
    await ddc.create_url_agency_links(
        url_ids=[url_id],
        agency_ids=[agency_id]
    )

    ## Optional DS Metadata
    optional_ds_metadata = URLOptionalDataSourceMetadata(
        url_id=url_id,
        record_formats=["csv", "pdf"],
        data_portal_type="CKAN",
        supplying_entity="ReadOnly Agency",
        coverage_start=date(year=2025, month=6, day=1),
        coverage_end=date(year=2025, month=8, day=20),
        agency_supplied=False,
        agency_originated=True,
        agency_aggregation=AgencyAggregationEnum.LOCALITY,
        agency_described_not_in_database="ReadOnly Agency Not In DB",
        update_method=UpdateMethodEnum.NO_UPDATES,
        readme_url="https://read-only-readme.com",
        originating_entity="ReadOnly Agency Originating",
        retention_schedule=RetentionScheduleEnum.GT_10_YEARS,
        scraper_url="https://read-only-scraper.com",
        submission_notes="Read Only Submission Notes",
        access_notes="Read Only Access Notes",
        access_types=[AccessTypeEnum.WEBPAGE, AccessTypeEnum.API],
    )
    await ddc.adb_client.add(optional_ds_metadata)

    ## DS App Link
    app_link = DSAppLinkDataSource(
        url_id=url_id,
        ds_data_source_id=1
    )
    await ddc.adb_client.add(app_link)

    return url_id
