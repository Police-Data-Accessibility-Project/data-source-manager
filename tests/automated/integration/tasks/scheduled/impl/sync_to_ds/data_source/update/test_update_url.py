from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.update import DSAppSyncDataSourcesUpdateTaskOperator
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel
from tests.helpers.run import run_task_and_confirm_success


async def test_update_url(
    ds_app_linked_data_source_url: DSAppLinkInfoModel,
    operator: DSAppSyncDataSourcesUpdateTaskOperator
):

    # Check prerequisites not met
    assert not await operator.meets_task_prerequisites()

    # Update URL table

    # Check prerequisites are met
    assert operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was called with expected parameters

    # Check DS App Link Is Updated

    raise NotImplementedError
