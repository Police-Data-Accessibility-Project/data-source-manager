from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.update.queries.get import \
    DSAppSyncAgenciesUpdateGetQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.update.queries.prereq import \
    DSAppSyncAgenciesUpdatePrerequisitesQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.update.queries.update_links import \
    DSAppSyncAgenciesUpdateAlterLinksQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.templates.operator import DSSyncTaskOperatorBase
from src.db.enums import TaskType
from src.external.pdap.impl.sync.agencies.update.core import UpdateAgenciesRequestBuilder
from src.external.pdap.impl.sync.agencies.update.request import UpdateAgenciesOuterRequest


class DSAppSyncAgenciesUpdateTaskOperator(
    DSSyncTaskOperatorBase
):

    @property
    def task_type(self) -> TaskType:
        return TaskType.SYNC_AGENCIES_UPDATE

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.run_query_builder(
            DSAppSyncAgenciesUpdatePrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:
        request: UpdateAgenciesOuterRequest = await self.get_inputs()
        await self.make_request(request)
        ds_app_ids: list[int] = [
            agency.app_id
            for agency in request.agencies
        ]
        await self.update_links(ds_app_ids)

    async def get_inputs(self) -> UpdateAgenciesOuterRequest:
        return await self.adb_client.run_query_builder(
            DSAppSyncAgenciesUpdateGetQueryBuilder()
        )

    async def make_request(
        self,
        request: UpdateAgenciesOuterRequest
    ):
        await self.pdap_client.run_request_builder(
            UpdateAgenciesRequestBuilder(request)
        )

    async def update_links(
        self,
        ds_app_ids: list[int]
    ) -> None:
        await self.adb_client.run_query_builder(
            DSAppSyncAgenciesUpdateAlterLinksQueryBuilder(
                ds_agency_ids=ds_app_ids
            )
        )