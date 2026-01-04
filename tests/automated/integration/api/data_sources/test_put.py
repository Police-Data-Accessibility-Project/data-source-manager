from datetime import date

import pytest

from src.api.endpoints.data_source.by_id.put.request import DataSourcePutRequest
from src.core.enums import RecordType
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.optional_ds_metadata.enums import AgencyAggregationEnum, UpdateMethodEnum, \
    RetentionScheduleEnum, AccessTypeEnum
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from tests.helpers.api_test_helper import APITestHelper


@pytest.mark.asyncio
async def test_put(
    api_test_helper: APITestHelper,
    test_url_data_source_id: int,
    test_batch_id: int
):

    api_test_helper.request_validator.put_v3(
        url=f"/data-sources/{test_url_data_source_id}",
        json=DataSourcePutRequest(
            url="http://modified_url.com/",
            name="Modified URL",
            record_type=RecordType.OTHER,

            batch_id=test_batch_id,
            description="Modified Description",

            record_formats=["csv", "pdf"],
            data_portal_type="CKAN",
            supplying_entity="Modified Supplying Entity",
            coverage_start=date(year=2025, month=4, day=1),
            coverage_end=date(year=2025, month=8, day=29),
            agency_supplied=False,
            agency_originated=True,
            agency_aggregation=AgencyAggregationEnum.LOCALITY,
            agency_described_not_in_database="Modified Agency Not In DB",
            update_method=UpdateMethodEnum.OVERWRITE,
            readme_url="https://modified-readme.com",
            originating_entity="Modified Originating Entity",
            retention_schedule=RetentionScheduleEnum.FUTURE_ONLY,
            scraper_url="https://modified-scraper.com",
            submission_notes="Modified Submission Notes",
            access_notes="Modified Access Notes",
            access_types=[AccessTypeEnum.WEBPAGE, AccessTypeEnum.API],
        ).model_dump(mode='json')

    )

    adb_client: AsyncDatabaseClient = api_test_helper.adb_client()

    url: URL = (await adb_client.get_all(URL))[0]
    assert url.url == "modified_url.com"
    assert url.scheme == "http"
    assert url.trailing_slash == True
    assert url.description == "Modified Description"

    # Check Record Type
    record_type: URLRecordType = (await adb_client.get_all(URLRecordType))[0]
    assert record_type.record_type == RecordType.OTHER

    # Check Batch Link
    link: LinkBatchURL = (await adb_client.get_all(LinkBatchURL))[0]
    assert link.batch_id == test_batch_id

    # Check Optional Metadata
    optional_metadata: URLOptionalDataSourceMetadata = (await adb_client.get_all(URLOptionalDataSourceMetadata))[0]
    assert optional_metadata.record_formats == ["csv", "pdf"]
    assert optional_metadata.data_portal_type == "CKAN"
    assert optional_metadata.supplying_entity == "Modified Supplying Entity"
    assert optional_metadata.coverage_start == date(year=2025, month=4, day=1)
    assert optional_metadata.coverage_end == date(year=2025, month=8, day=29)
    assert optional_metadata.agency_supplied == False
    assert optional_metadata.agency_originated == True
    assert optional_metadata.agency_aggregation == AgencyAggregationEnum.LOCALITY
    assert optional_metadata.agency_described_not_in_database == "Modified Agency Not In DB"
    assert optional_metadata.update_method == UpdateMethodEnum.OVERWRITE
    assert optional_metadata.readme_url == "https://modified-readme.com"
    assert optional_metadata.originating_entity == "Modified Originating Entity"
    assert optional_metadata.retention_schedule == RetentionScheduleEnum.FUTURE_ONLY
    assert optional_metadata.scraper_url == "https://modified-scraper.com"
    assert optional_metadata.submission_notes == "Modified Submission Notes"
    assert optional_metadata.access_notes == "Modified Access Notes"
    assert optional_metadata.access_types == [AccessTypeEnum.WEBPAGE, AccessTypeEnum.API]
