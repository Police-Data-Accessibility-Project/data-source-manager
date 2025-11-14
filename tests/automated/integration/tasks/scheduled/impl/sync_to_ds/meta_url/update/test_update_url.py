from sqlalchemy import update

from src.api.shared.models.message_response import MessageResponse
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.update.core import DSAppSyncMetaURLsUpdateTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL
from src.external.pdap.client import PDAPClient
from src.external.pdap.impl.sync.meta_urls._shared.content import MetaURLSyncContentModel
from src.external.pdap.impl.sync.meta_urls.update.request import UpdateMetaURLsOuterRequest, UpdateMetaURLsInnerRequest
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.helpers import extract_and_validate_sync_request, \
    mock_make_request
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel
from tests.helpers.run import run_task_and_confirm_success


async def test_update_url(
    ds_app_linked_meta_url: DSAppLinkInfoModel,
    operator: DSAppSyncMetaURLsUpdateTaskOperator,
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
            URL.id == ds_app_linked_meta_url.db_id
        )
    )
    await adb_client_test.execute(statement)

    # Check prerequisites are met
    assert operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was called with expected parameters
    request: UpdateMetaURLsOuterRequest = extract_and_validate_sync_request(
        mock_pdap_client,
        expected_path="meta-urls/update",
        expected_model=UpdateMetaURLsOuterRequest
    )
    assert len(request.meta_urls) == 1
    meta_url: UpdateMetaURLsInnerRequest = request.meta_urls[0]
    assert meta_url.app_id == ds_app_linked_meta_url.ds_app_id
    content: MetaURLSyncContentModel = meta_url.content
    assert content.url == "http://modified-example.com/"
    assert set(content.agency_ids) == {test_agency_id}

    # Check DS App Link Is Updated
    ds_app_link: DSAppLinkMetaURL | None = await adb_client_test.one_or_none_model(model=DSAppLinkMetaURL)
    assert ds_app_link is not None
    assert ds_app_link.ds_meta_url_id == 67
    assert ds_app_link.last_synced_at > ds_app_linked_meta_url.updated_at

