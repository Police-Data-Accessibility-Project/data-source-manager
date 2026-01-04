from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest
from pdap_access_manager.models.response import ResponseInfo

from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.scheduled.impl.sync_from_ds.impl.follows.core import DSAppSyncUserFollowsGetTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.link.location__user_follow import LinkLocationUserFollow
from src.external.pdap.client import PDAPClient
from src.external.pdap.impl.sync.follows.response import SyncFollowGetInnerResponse, SyncFollowGetOuterResponse
from tests.automated.integration.conftest import MOCK_USER_ID
from tests.helpers.asserts import assert_task_run_success
from tests.helpers.data_creator.models.creation_info.county import CountyCreationInfo
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo


def mock_client(
    mock_pdap_client: PDAPClient,
    response: list[SyncFollowGetInnerResponse]
) -> None:
    mock_pdap_client.access_manager.make_request = AsyncMock(
        return_value=ResponseInfo(
            status_code=HTTPStatus.OK,
            data=SyncFollowGetOuterResponse(
                follows=response
            ).model_dump(mode='json')
        )
    )

@pytest.mark.asyncio
async def test_core(
    adb_client_test: AsyncDatabaseClient,
    mock_pdap_client: PDAPClient,
    pittsburgh_locality: LocalityCreationInfo,
    allegheny_county: CountyCreationInfo,
    pennsylvania: USStateCreationInfo
):
    operator = DSAppSyncUserFollowsGetTaskOperator(
        adb_client=adb_client_test,
        pdap_client=mock_pdap_client
    )

    # Mock client to add 3 new follows
    mock_client(
        mock_pdap_client,
        response=[
            SyncFollowGetInnerResponse(
                user_id=MOCK_USER_ID,
                location_id=pittsburgh_locality.location_id
            ),
            SyncFollowGetInnerResponse(
                user_id=MOCK_USER_ID,
                location_id=allegheny_county.location_id
            ),
            SyncFollowGetInnerResponse(
                user_id=MOCK_USER_ID,
                location_id=pennsylvania.location_id
            )
        ]
    )

    # # Run Task
    run_info: TaskOperatorRunInfo = await operator.run_task()
    assert_task_run_success(run_info)

    # confirm three follows added
    links: list[LinkLocationUserFollow] = await adb_client_test.get_all(LinkLocationUserFollow)
    assert len(links) == 3
    link_tuples = [(link.user_id, link.location_id) for link in links]
    assert (MOCK_USER_ID, pittsburgh_locality.location_id) in link_tuples
    assert (MOCK_USER_ID, allegheny_county.location_id) in link_tuples
    assert (MOCK_USER_ID, pennsylvania.location_id) in link_tuples

    # # Run Task again
    run_info: TaskOperatorRunInfo = await operator.run_task()
    assert_task_run_success(run_info)

    # # Confirm no new follows added
    links: list[LinkLocationUserFollow] = await adb_client_test.get_all(LinkLocationUserFollow)
    assert len(links) == 3
    link_tuples = [(link.user_id, link.location_id) for link in links]
    assert (MOCK_USER_ID, pittsburgh_locality.location_id) in link_tuples
    assert (MOCK_USER_ID, allegheny_county.location_id) in link_tuples
    assert (MOCK_USER_ID, pennsylvania.location_id) in link_tuples


    # Mock client to add only two of the follows
    mock_client(
        mock_pdap_client,
        response=[
            SyncFollowGetInnerResponse(
                user_id=MOCK_USER_ID,
                location_id=pittsburgh_locality.location_id
            ),
            SyncFollowGetInnerResponse(
                user_id=MOCK_USER_ID,
                location_id=allegheny_county.location_id
            ),
        ]
    )

    # # Run Task again
    run_info: TaskOperatorRunInfo = await operator.run_task()
    assert_task_run_success(run_info)
    # Confirm one of the follows is removed

    links: list[LinkLocationUserFollow] = await adb_client_test.get_all(LinkLocationUserFollow)
    assert len(links) == 2
    link_tuples = [(link.user_id, link.location_id) for link in links]
    assert (MOCK_USER_ID, pittsburgh_locality.location_id) in link_tuples
    assert (MOCK_USER_ID, allegheny_county.location_id) in link_tuples

