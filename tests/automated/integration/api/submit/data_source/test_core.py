from datetime import date
from uuid import UUID

import pytest

from src.api.endpoints.submit.data_source.request import DataSourceSubmissionRequest
from src.core.enums import RecordType, BatchStatus
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.annotation.agency.anon.sqlalchemy import AnnotationAgencyAnon
from src.db.models.impl.annotation.location.anon.sqlalchemy import AnnotationLocationAnon
from src.db.models.impl.annotation.name.suggestion.sqlalchemy import AnnotationNameSuggestion
from src.db.models.impl.annotation.record_type.anon.sqlalchemy import AnnotationRecordTypeAnon
from src.db.models.impl.annotation.url_type.anon.sqlalchemy import AnnotationURLTypeAnon
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.optional_ds_metadata.enums import AgencyAggregationEnum, UpdateMethodEnum, \
    RetentionScheduleEnum, AccessTypeEnum
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo


@pytest.mark.asyncio
async def test_submit_data_source(
    api_test_helper: APITestHelper,
    test_agency_id: int,
    pittsburgh_locality: LocalityCreationInfo,
):
    ath = api_test_helper
    ath.request_validator.post_v3(
        url="submit/data-source",
        json=DataSourceSubmissionRequest(
            source_url="https://example.com/",
            name="Example name",
            description="Example description",
            record_type=RecordType.COMPLAINTS_AND_MISCONDUCT,
            coverage_start=date(year=2025, month=8, day=9),
            coverage_end=date(year=2025, month=8, day=10),
            supplying_entity="Test supplying entity",
            agency_supplied=True,
            agency_originated=False,
            agency_aggregation=AgencyAggregationEnum.STATE,
            agency_described_not_in_database="Test agency described not in database",
            update_method=UpdateMethodEnum.NO_UPDATES,
            readme_url="https://example.com/readme",
            originating_entity="Test Originating Entity",
            retention_schedule=RetentionScheduleEnum.GT_10_YEARS,
            scraper_url="https://example.com/scraper",
            submission_notes="Test submission notes",
            data_portal_type="Test data portal",
            access_notes="Test access notes",
            access_types=[
                AccessTypeEnum.API,
                AccessTypeEnum.DOWNLOAD,
                AccessTypeEnum.WEBPAGE
            ],
            record_formats=[
                "Test record format",
                "Test record format 2"
            ],

            agency_ids=[test_agency_id],
            location_ids=[pittsburgh_locality.location_id]

        ).model_dump(mode='json')
    )

    adb_client: AsyncDatabaseClient = api_test_helper.adb_client()

    # Check URL
    url: URL = await adb_client.one_or_none_model(URL)
    assert url is not None
    assert url.url == "example.com"
    assert url.scheme == "https"
    assert url.trailing_slash == True
    assert url.source == URLSource.MANUAL
    assert url.description == "Example description"

    # Check for Batch
    batch: Batch = await adb_client.one_or_none_model(Batch)
    assert batch is not None
    assert batch.user_id is None
    assert batch.strategy == 'manual'
    assert batch.status == BatchStatus.READY_TO_LABEL.value
    assert batch.parameters == {}

    # Check for Batch URL Link
    batch_url_link: LinkBatchURL = await adb_client.one_or_none_model(LinkBatchURL)
    assert batch_url_link is not None
    assert batch_url_link.batch_id == batch.id
    assert batch_url_link.url_id == url.id

    # Check for anonymous annotations
    url_type_suggestion: AnnotationURLTypeAnon = await adb_client.one_or_none_model(AnnotationURLTypeAnon)
    assert url_type_suggestion is not None
    assert url_type_suggestion.url_id == url.id
    assert url_type_suggestion.url_type == URLType.DATA_SOURCE
    session_id: UUID = url_type_suggestion.session_id

    # Check for Location Suggestion
    location_suggestion: AnnotationLocationAnon = await adb_client.one_or_none_model(AnnotationLocationAnon)
    assert location_suggestion is not None
    assert location_suggestion.location_id == pittsburgh_locality.location_id
    assert location_suggestion.session_id == session_id

    # Check for Agency Suggestion
    agency_suggestion: AnnotationAgencyAnon = await adb_client.one_or_none_model(AnnotationAgencyAnon)
    assert agency_suggestion is not None
    assert agency_suggestion.agency_id == test_agency_id
    assert agency_suggestion.session_id == session_id

    # Check for Name Suggestion
    name_suggestion: AnnotationNameSuggestion = await adb_client.one_or_none_model(AnnotationNameSuggestion)
    assert name_suggestion is not None
    assert name_suggestion.suggestion == "Example name"

    # Check for Record Type Suggestion
    record_type_suggestion: AnnotationRecordTypeAnon = await adb_client.one_or_none_model(AnnotationRecordTypeAnon)
    assert record_type_suggestion.record_type == RecordType.COMPLAINTS_AND_MISCONDUCT
    assert record_type_suggestion.session_id == session_id

    # Check for URL DS Optional Metadata
    optional_ds: URLOptionalDataSourceMetadata = await adb_client.one_or_none_model(URLOptionalDataSourceMetadata)
    assert optional_ds is not None
    assert optional_ds.coverage_start == date(year=2025, month=8, day=9)
    assert optional_ds.coverage_end == date(year=2025, month=8, day=10)
    assert optional_ds.supplying_entity == "Test supplying entity"
    assert optional_ds.agency_supplied
    assert not optional_ds.agency_originated
    assert optional_ds.agency_aggregation == AgencyAggregationEnum.STATE
    assert optional_ds.agency_described_not_in_database == "Test agency described not in database"
    assert optional_ds.data_portal_type == "Test data portal"
    assert optional_ds.update_method == UpdateMethodEnum.NO_UPDATES
    assert optional_ds.readme_url == "https://example.com/readme"
    assert optional_ds.originating_entity == "Test Originating Entity"
    assert optional_ds.retention_schedule == RetentionScheduleEnum.GT_10_YEARS
    assert optional_ds.scraper_url == "https://example.com/scraper"
    assert optional_ds.submission_notes == "Test submission notes"
    assert optional_ds.access_notes == "Test access notes"
    assert optional_ds.access_types == [
        AccessTypeEnum.API,
        AccessTypeEnum.DOWNLOAD,
        AccessTypeEnum.WEBPAGE
    ]
    assert optional_ds.record_formats == [
        "Test record format",
        "Test record format 2"
    ]

