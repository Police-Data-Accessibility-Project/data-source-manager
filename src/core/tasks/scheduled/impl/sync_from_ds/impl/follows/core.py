from src.core.tasks.scheduled.impl.sync_from_ds.impl.follows.models.user_location_pairs import UserLocationPairs
from src.core.tasks.scheduled.impl.sync_from_ds.impl.follows.query import UpdateFollowsInDBQueryBuilder
from src.core.tasks.scheduled.impl.sync_from_ds.impl.follows.types import UserID, LocationID
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.external.pdap.client import PDAPClient
from src.external.pdap.impl.sync.follows.core import GetFollowsRequestBuilder
from src.external.pdap.impl.sync.follows.response import SyncFollowGetInnerResponse


class DSAppSyncUserFollowsGetTaskOperator(ScheduledTaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        pdap_client: PDAPClient
    ):
        super().__init__(adb_client)
        self.pdap_client = pdap_client

    @property
    def task_type(self) -> TaskType:
        return TaskType.SYNC_USER_FOLLOWS_GET

    async def inner_task_logic(self) -> None:
        responses = await self._get_follows_from_ds()
        await self._update_follows_in_db(responses)

    async def _get_follows_from_ds(self) -> list[SyncFollowGetInnerResponse]:
        return await self.pdap_client.run_request_builder(
            GetFollowsRequestBuilder()
        )

    async def _update_follows_in_db(self, responses: list[SyncFollowGetInnerResponse]) -> None:
        # Get response tuples
        api_pairs: list[UserLocationPairs] = [
            UserLocationPairs(
                user_id=UserID(response.user_id),
                location_id=LocationID(response.location_id)
            )
            for response in responses
        ]
        # Run query
        await self.adb_client.run_query_builder(
            UpdateFollowsInDBQueryBuilder(api_pairs=api_pairs)
        )
    #
    # async def _get_follows_in_db(self) -> list[tuple[int, int]]:
    #     query = (
    #         select(
    #             LinkLocationUserFollow.user_id,
    #             LinkLocationUserFollow.location_id
    #         )
    #     )
    #     mappings: Sequence[RowMapping] = await self.adb_client.mappings(query)