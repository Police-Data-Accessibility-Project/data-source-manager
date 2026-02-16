from datetime import date

from src.api.shared.models.message_response import MessageResponse
from src.core.enums import RecordType
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.update.core import \
    DSAppSyncDataSourcesUpdateTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from src.db.models.impl.url.optional_ds_metadata.enums import AgencyAggregationEnum, AccessTypeEnum, UpdateMethodEnum, \
    RetentionScheduleEnum
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.external.pdap.client import PDAPClient
from src.external.pdap.impl.sync.data_sources._shared.content import DataSourceSyncContentModel
from src.external.pdap.impl.sync.data_sources.update.request import UpdateDataSourcesInnerRequest, \
    UpdateDataSourcesOuterRequest
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.helpers import extract_and_validate_sync_request, \
    mock_make_request
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel
from tests.helpers.run import run_task_and_confirm_success


async def test_update_optional_ds_metadata(
    ds_app_linked_data_source_url: DSAppLinkInfoModel,
    operator: DSAppSyncDataSourcesUpdateTaskOperator,
    mock_pdap_client: PDAPClient,
    adb_client_test: AsyncDatabaseClient,
    test_agency_id: int
):
    # Mock make_request
    mock_make_request(
        mock_pdap_client=mock_pdap_client,
        data=MessageResponse(message="Success")
    )

    # Check prerequisites not met
    assert not await operator.meets_task_prerequisites()

    # Update url_optional_ds_metadata_table table
    insert = URLOptionalDataSourceMetadata(
        url_id=ds_app_linked_data_source_url.db_id,
        record_formats=["Record Format 1", "Record Format 2"],
        data_portal_type="Test Data Portal Type",
        supplying_entity="Test Supplying Entity",
        coverage_start=date(year=2025, month=5, day=1),
        coverage_end=date(year=2025, month=5, day=31),
        agency_supplied=True,
        agency_originated=True,
        agency_aggregation=AgencyAggregationEnum.FEDERAL,
        update_method=UpdateMethodEnum.OVERWRITE,
        readme_url="https://example.com/readme",
        originating_entity="Test originating entity",
        retention_schedule=RetentionScheduleEnum.FUTURE_ONLY,
        scraper_url="https://example.com/scraper",
        submission_notes="Test submission notes",
        access_notes="Test Access notes",
        access_types=[AccessTypeEnum.DOWNLOAD],
        data_portal_type_other="Test data portal type other"
    )
    await adb_client_test.add(insert)

    # Check prerequisites are met
    assert operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was called with expected parameters
    request: UpdateDataSourcesOuterRequest = extract_and_validate_sync_request(
        mock_pdap_client,
        expected_path="data-sources/update",
        expected_model=UpdateDataSourcesOuterRequest
    )
    assert len(request.data_sources) == 1
    data_source: UpdateDataSourcesInnerRequest = request.data_sources[0]
    assert data_source.app_id == ds_app_linked_data_source_url.ds_app_id
    content: DataSourceSyncContentModel = data_source.content
    assert content.source_url.startswith("https://example.com/")
    assert content.name.startswith("Example ")
    assert content.record_type == RecordType.CRIME_STATISTICS
    assert content.description is None
    assert content.record_formats == ["Record Format 1", "Record Format 2"]
    assert content.data_portal_type == "Test Data Portal Type"
    assert content.supplying_entity == "Test Supplying Entity"
    assert content.coverage_start == date(year=2025, month=5, day=1)
    assert content.coverage_end == date(year=2025, month=5, day=31)
    assert content.detail_level is None
    assert content.agency_supplied == True
    assert content.agency_originated == True
    assert content.update_method == UpdateMethodEnum.OVERWRITE
    assert content.readme_url == "https://example.com/readme"
    assert content.originating_entity == "Test originating entity"
    assert content.retention_schedule == RetentionScheduleEnum.FUTURE_ONLY
    assert content.scraper_url == "https://example.com/scraper"
    assert content.access_notes == "Test Access notes"
    assert content.access_types == [AccessTypeEnum.DOWNLOAD]
    assert content.data_portal_type_other == "Test data portal type other"

    # Check DS App Link Is Updated
    ds_app_link: DSAppLinkDataSource | None = await adb_client_test.one_or_none_model(model=DSAppLinkDataSource)
    assert ds_app_link is not None
    assert ds_app_link.ds_data_source_id == 67
    assert ds_app_link.last_synced_at > ds_app_linked_data_source_url.updated_at

