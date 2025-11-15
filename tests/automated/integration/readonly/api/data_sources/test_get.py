from datetime import date

import pytest
from deepdiff import DeepDiff

from src.api.endpoints.data_source.get.response import DataSourceGetOuterResponse, DataSourceGetResponse
from src.core.enums import RecordType
from src.db.models.impl.url.optional_ds_metadata.enums import AgencyAggregationEnum, UpdateMethodEnum, \
    RetentionScheduleEnum, AccessTypeEnum
from tests.automated.integration.readonly.helper import ReadOnlyTestHelper


@pytest.mark.asyncio
async def test_get(readonly_helper: ReadOnlyTestHelper):

    raw_json: dict = readonly_helper.api_test_helper.request_validator.get_v3(
        url=f"/data-sources",
    )
    outer_response = DataSourceGetOuterResponse(**raw_json)

    assert len(outer_response.results) == 2
    response: DataSourceGetResponse = outer_response.results[0]

    diff = DeepDiff(
        response.model_dump(mode='json'),
        DataSourceGetResponse(
            url_id=readonly_helper.maximal_data_source,
            url="read-only-ds.com",

            name="Read only URL name",
            record_type=RecordType.CRIME_STATISTICS,
            agency_ids=[readonly_helper.agency_1_id],

            batch_id=None,
            description="Read only URL",

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
        ).model_dump(mode='json'),
    )

    assert diff == {}, f"Differences found: {diff}"
