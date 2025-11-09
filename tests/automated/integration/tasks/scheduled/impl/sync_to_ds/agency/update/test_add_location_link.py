from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.update.core import DSAppSyncAgenciesUpdateTaskOperator
from tests.automated.integration.tasks.scheduled.impl.sync_to_ds.models.ds_app_link_info import DSAppLinkInfoModel
from tests.helpers.data_creator.models.creation_info.county import CountyCreationInfo
from tests.helpers.run import run_task_and_confirm_success


async def test_add_location_link(
    ds_app_linked_agency: DSAppLinkInfoModel,
    allegheny_county: CountyCreationInfo,
    operator: DSAppSyncAgenciesUpdateTaskOperator
):


    # Check prerequisites not met
    assert not await operator.meets_task_prerequisites()

    # Add location link

    # Check prerequisites are met
    assert operator.meets_task_prerequisites()

    # Run task and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm expected method was called with expected parameters

    # Check DS App Link Is Updated

    raise NotImplementedError
