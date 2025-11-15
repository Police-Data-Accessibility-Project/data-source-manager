from datetime import date

from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.agency.enums import AgencyType, JurisdictionType
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.optional_ds_metadata.enums import AgencyAggregationEnum, UpdateMethodEnum, \
    RetentionScheduleEnum, AccessTypeEnum
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from tests.automated.integration.readonly.helper import ReadOnlyTestHelper
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.county import CountyCreationInfo
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo


async def setup_readonly_data(
    api_test_helper: APITestHelper
) -> ReadOnlyTestHelper:
    db_data_creator = api_test_helper.db_data_creator
    adb_client = db_data_creator.adb_client

    # Pennsylvania
    pennsylvania: USStateCreationInfo = await db_data_creator.create_us_state(
        name="Pennsylvania",
        iso="PA"
    )
    allegheny_county: CountyCreationInfo = await db_data_creator.create_county(
        state_id=pennsylvania.us_state_id,
        name="Allegheny"
    )
    pittsburgh: LocalityCreationInfo = await db_data_creator.create_locality(
        state_id=pennsylvania.us_state_id,
        county_id=allegheny_county.county_id,
        name="Pittsburgh"
    )


    # Add Agencies
    agency_1_id: int = await add_agency(adb_client, pittsburgh.location_id)
    agency_2_id: int = await add_agency(adb_client, allegheny_county.location_id)

    # Add Data Source With Linked Agency
    maximal_data_source: int = await add_maximal_data_source(
        agency_1_id=agency_1_id,
        db_data_creator=db_data_creator
    )
    minimal_data_source: int = await add_minimal_data_source(
        agency_1_id=agency_1_id,
        db_data_creator=db_data_creator
    )

    # Add Meta URL with Linked Agency
    url_meta_url_id: int = await add_meta_url(agency_1_id, db_data_creator)

    return ReadOnlyTestHelper(
        adb_client=adb_client,
        api_test_helper=api_test_helper,

        agency_1_id=agency_1_id,
        agency_1_location_id=pittsburgh.location_id,

        agency_2_id=agency_2_id,
        agency_2_location_id=allegheny_county.location_id,

        maximal_data_source=maximal_data_source,
        minimal_data_source=minimal_data_source,
        url_meta_url_id=url_meta_url_id,
    )


async def add_meta_url(
    agency_1_id: int,
    db_data_creator: DBDataCreator
) -> int:
    adb_client: AsyncDatabaseClient = db_data_creator.adb_client
    url = URL(
        scheme=None,
        url="read-only-meta-url.com",
        name="Read only URL Name",
        trailing_slash=False,
        description="Read only URL",
        collector_metadata={
            "url": "https://read-only-meta-url.com/"
        },
        status=URLStatus.OK,
        source=URLSource.REDIRECT,
    )
    url_id: int = await adb_client.add(url, return_id=True)

    await db_data_creator.create_validated_flags(
        url_ids=[url_id],
        validation_type=URLType.META_URL
    )

    return url_id


async def add_maximal_data_source(
    agency_1_id: int,
    db_data_creator: DBDataCreator
) -> int:
    adb_client: AsyncDatabaseClient = db_data_creator.adb_client
    url = URL(
        scheme="https",
        url="read-only-ds.com",
        name="Read only URL name",
        trailing_slash=True,
        description="Read only URL",
        collector_metadata={
            "url": "https://read-only.com/"
        },
        status=URLStatus.OK,
        source=URLSource.COLLECTOR,
    )
    url_id: int = await adb_client.add(url, return_id=True)
    await db_data_creator.create_validated_flags(
        url_ids=[url_id],
        validation_type=URLType.DATA_SOURCE
    )
    record_type = URLRecordType(
        url_id=url_id,
        record_type=RecordType.CRIME_STATISTICS
    )
    await adb_client.add(record_type)

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

    await adb_client.add(optional_ds_metadata)

    await db_data_creator.create_url_agency_links(
        url_ids=[url_id],
        agency_ids=[agency_1_id]
    )
    return url_id

async def add_minimal_data_source(
    agency_1_id: int,
    db_data_creator: DBDataCreator
) -> int:
    adb_client: AsyncDatabaseClient = db_data_creator.adb_client
    url = URL(
        scheme="https",
        url="minimal-ds.com",
        name="Minimal name",
        trailing_slash=False,
        collector_metadata={},
        status=URLStatus.OK,
        source=URLSource.ROOT_URL,
    )
    url_id: int = await adb_client.add(url, return_id=True)
    await db_data_creator.create_validated_flags(
        url_ids=[url_id],
        validation_type=URLType.DATA_SOURCE
    )
    record_type = URLRecordType(
        url_id=url_id,
        record_type=RecordType.POLICIES_AND_CONTRACTS
    )
    await adb_client.add(record_type)

    await db_data_creator.create_url_agency_links(
        url_ids=[url_id],
        agency_ids=[agency_1_id]
    )
    return url_id


async def add_agency(
    adb_client: AsyncDatabaseClient,
    location_id: int
) -> int:
    agency_1 = Agency(
        name="Agency 1",
        agency_type=AgencyType.LAW_ENFORCEMENT,
        jurisdiction_type=JurisdictionType.STATE,
    )
    agency_id: int = await adb_client.add(agency_1, return_id=True)
    # Add Agency location
    agency_1_location = LinkAgencyLocation(
        agency_id=agency_id,
        location_id=location_id,
    )
    await adb_client.add(agency_1_location)
    return agency_id