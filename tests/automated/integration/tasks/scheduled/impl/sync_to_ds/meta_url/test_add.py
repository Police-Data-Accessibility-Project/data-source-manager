import pytest

from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.add.core import DSAppSyncMetaURLsAddTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL
from src.external.pdap.client import PDAPClient
from src.external.pdap.impl.sync.meta_urls._shared.content import MetaURLSyncContentModel
from src.external.pdap.impl.sync.meta_urls.add.request import AddMetaURLsOuterRequest, AddMetaURLsInnerRequest
from src.external.pdap.impl.sync.shared.models.add.response import DSAppSyncAddResponseModel, \
    DSAppSyncAddResponseInnerModel
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.helpers import extract_and_validate_sync_request, \
    mock_make_request
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_add(
    db_data_creator: DBDataCreator,
    test_url_meta_url_id: int,
    adb_client_test: AsyncDatabaseClient,
    mock_pdap_client: PDAPClient,
    test_agency_id: int
):
    operator = DSAppSyncMetaURLsAddTaskOperator(
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
                    request_id=test_url_meta_url_id
                )
            ]
        )
    )


    # Check meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was called with expected parameters
    request: AddMetaURLsOuterRequest = extract_and_validate_sync_request(
        mock_pdap_client,
        expected_path="meta-urls/add",
        expected_model=AddMetaURLsOuterRequest
    )
    assert len(request.meta_urls) == 1
    meta_url: AddMetaURLsInnerRequest = request.meta_urls[0]
    assert meta_url.request_id == test_url_meta_url_id
    content: MetaURLSyncContentModel = meta_url.content
    assert content.url.startswith("https://example.com/")
    assert content.agency_ids == [test_agency_id]

    # Check Presence of DS Meta URL App Link
    ds_app_link: DSAppLinkMetaURL | None = await adb_client_test.one_or_none_model(model=DSAppLinkMetaURL)
    assert ds_app_link is not None
    assert ds_app_link.ds_meta_url_id == 67
    assert ds_app_link.url_id == test_url_meta_url_id
