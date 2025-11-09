from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.update.core import DSAppSyncAgenciesUpdateTaskOperator
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo
from tests.helpers.run import run_task_and_confirm_success


async def test_delete_location_link(
    ds_app_linked_agency: DSAppLinkInfoModel,
    pittsburgh_locality: LocalityCreationInfo,
    operator: DSAppSyncAgenciesUpdateTaskOperator
):

    # Check prerequisites not met
    assert not await operator.meets_task_prerequisites()

    # Delete location link

    # Check prerequisites are met
    assert operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was called with expected parameters

    # Check DS App Link Is Updated

    raise NotImplementedError
