from datetime import date

import pytest
from deepdiff import DeepDiff

from src.api.endpoints.data_source.get.response import DataSourceGetOuterResponse, DataSourceGetResponse, \
    DataSourceURLHealthResponse
from src.core.enums import RecordType
from src.db.models.impl.url.optional_ds_metadata.enums import AgencyAggregationEnum, UpdateMethodEnum, \
    RetentionScheduleEnum, AccessTypeEnum
from src.db.models.materialized_views.url_health.enums import URLHealthViewEnum
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
            url_id=readonly_helper.maximal_data_source_url_id,
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
            update_method=UpdateMethodEnum.NO_UPDATES,
            readme_url="https://read-only-readme.com",
            originating_entity="ReadOnly Agency Originating",
            retention_schedule=RetentionScheduleEnum.GT_10_YEARS,
            scraper_url="https://read-only-scraper.com",
            submission_notes="Read Only Submission Notes",
            access_notes="Read Only Access Notes",
            access_types=[AccessTypeEnum.WEBPAGE, AccessTypeEnum.API],
            url_health=DataSourceURLHealthResponse(
                value=URLHealthViewEnum.BROKEN,
                code=300,
                http_status_code=None,
                redirect_url_id=None,
                redirect_url=None,
                redirect_http_status_code=None,
                has_redirect=False,
                redirect_is_healthy=False,
                has_archive=False,
                archive_url=None,
            ),
        ).model_dump(mode='json'),
    )

    assert diff == {}, f"Differences found: {diff}"
