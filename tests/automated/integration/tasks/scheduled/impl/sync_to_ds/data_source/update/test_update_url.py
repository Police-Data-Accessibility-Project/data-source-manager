from sqlalchemy import update

from src.api.shared.models.message_response import MessageResponse
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.update.core import \
    DSAppSyncDataSourcesUpdateTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from src.external.pdap.client import PDAPClient
from src.external.pdap.impl.sync.data_sources._shared.content import DataSourceSyncContentModel
from src.external.pdap.impl.sync.data_sources.update.request import UpdateDataSourcesInnerRequest, \
    UpdateDataSourcesOuterRequest
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.helpers import extract_and_validate_sync_request, \
    mock_make_request
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel
from tests.helpers.run import run_task_and_confirm_success


async def test_update_url(
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

    # Update URL table
    statement = (
        update(
            URL
        )
        .values(
            name="Updated URL Name",
            scheme="http",
            trailing_slash=True,
            url="modified-example.com",
            description="Updated URL Description",
        )
        .where(
            URL.id == ds_app_linked_data_source_url.db_id
        )
    )
    await adb_client_test.execute(statement)

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
    assert content.name == "Updated URL Name"
    assert content.agency_ids == [
        test_agency_id
    ]
    assert content.source_url == "http://modified-example.com/"
    assert content.description == "Updated URL Description"

    # Check DS App Link Is Updated
    ds_app_link: DSAppLinkDataSource | None = await adb_client_test.one_or_none_model(model=DSAppLinkDataSource)
    assert ds_app_link is not None
    assert ds_app_link.ds_data_source_id == 67
    assert ds_app_link.last_synced_at > ds_app_linked_data_source_url.updated_at

