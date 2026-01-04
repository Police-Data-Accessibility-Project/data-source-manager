from datetime import date

from src.core.enums import RecordType
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.optional_ds_metadata.enums import AgencyAggregationEnum, UpdateMethodEnum, \
    RetentionScheduleEnum, AccessTypeEnum
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from tests.helpers.data_creator.core import DBDataCreator


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
