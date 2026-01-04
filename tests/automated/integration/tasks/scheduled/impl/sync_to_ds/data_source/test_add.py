import pytest

from src.core.enums import RecordType
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.add.core import DSAppSyncDataSourcesAddTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from src.external.pdap.client import PDAPClient
from src.external.pdap.impl.sync.data_sources._shared.content import DataSourceSyncContentModel
from src.external.pdap.impl.sync.data_sources.add.request import AddDataSourcesOuterRequest, AddDataSourcesInnerRequest
from src.external.pdap.impl.sync.shared.models.add.response import DSAppSyncAddResponseModel, \
    DSAppSyncAddResponseInnerModel
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.helpers import extract_and_validate_sync_request, \
    mock_make_request
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_add(
    db_data_creator: DBDataCreator,
    test_url_data_source_id: int,
    adb_client_test: AsyncDatabaseClient,
    mock_pdap_client: PDAPClient,
    test_agency_id: int
):
    operator = DSAppSyncDataSourcesAddTaskOperator(
        adb_client=adb_client_test,
        pdap_client=mock_pdap_client
    )

    # Mock make_request
    mock_make_request(
        mock_pdap_client=mock_pdap_client,
        data=DSAppSyncAddResponseModel(
            entities=[
                DSAppSyncAddResponseInnerModel(
                    app_id=67,
                    request_id=test_url_data_source_id
                )
            ]
        )
    )

    # Check meet task prerequisites
    assert await operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was called with expected parameters
    request: AddDataSourcesOuterRequest = extract_and_validate_sync_request(
        mock_pdap_client,
        expected_path="data-sources/add",
        expected_model=AddDataSourcesOuterRequest
    )
    assert len(request.data_sources) == 1
    data_source: AddDataSourcesInnerRequest = request.data_sources[0]
    assert data_source.request_id == test_url_data_source_id
    content: DataSourceSyncContentModel = data_source.content
    assert content.source_url.startswith("https://example.com/")
    assert content.name.startswith("Example ")
    assert content.record_type == RecordType.CRIME_STATISTICS
    assert content.description is None
    assert content.record_formats == []
    assert content.data_portal_type is None
    assert content.supplying_entity is None
    assert content.coverage_start is None
    assert content.coverage_end is None
    assert content.detail_level is None
    assert content.agency_supplied is None
    assert content.agency_originated is None
    assert content.agency_described_not_in_database is None
    assert content.update_method is None
    assert content.readme_url is None
    assert content.originating_entity is None
    assert content.retention_schedule is None
    assert content.scraper_url is None
    assert content.access_notes is None
    assert content.access_types == []
    assert content.data_portal_type_other is None

    assert content.agency_ids == [test_agency_id]

    # Check Presence of DS App Link
    ds_app_link: DSAppLinkDataSource | None = await adb_client_test.one_or_none_model(DSAppLinkDataSource)
    assert ds_app_link is not None
    assert ds_app_link.ds_data_source_id == 67
    assert ds_app_link.url_id == test_url_data_source_id
