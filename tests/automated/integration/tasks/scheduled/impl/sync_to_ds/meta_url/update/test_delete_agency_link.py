from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.update.core import DSAppSyncMetaURLsUpdateTaskOperator
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel
from tests.helpers.run import run_task_and_confirm_success


async def test_delete_agency_link(
    ds_app_linked_meta_url: DSAppLinkInfoModel,
    test_agency_id_1: int,
    operator: DSAppSyncMetaURLsUpdateTaskOperator
):

    # Check prerequisites not met
    assert not await operator.meets_task_prerequisites()

    # Delete agency link

    # Check prerequisites are met
    assert operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was called with expected parameters

    # Check DS App Link Is Updated

    raise NotImplementedError
