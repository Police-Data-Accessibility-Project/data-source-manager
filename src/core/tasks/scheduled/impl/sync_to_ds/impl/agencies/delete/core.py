from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.delete.queries.delete_flags import \
    DSAppSyncAgenciesDeleteRemoveFlagsQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.delete.queries.delete_links import \
    DSAppSyncAgenciesDeleteRemoveLinksQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.delete.queries.get import \
    DSAppSyncAgenciesDeleteGetQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.delete.queries.prereq import \
    DSAppSyncAgenciesDeletePrerequisitesQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.templates.operator import DSSyncTaskOperatorBase
from src.db.enums import TaskType
from src.external.pdap.impl.sync.agencies.delete.core import DeleteAgenciesRequestBuilder


class DSAppSyncAgenciesDeleteTaskOperator(
    DSSyncTaskOperatorBase
):

    @property
    def task_type(self) -> TaskType:
        return TaskType.SYNC_AGENCIES_DELETE

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.run_query_builder(
            DSAppSyncAgenciesDeletePrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:
        ds_app_ids: list[int] = await self.get_inputs()
        await self.log_ds_app_ids(ds_app_ids)
        await self.make_request(ds_app_ids)
        await self.delete_flags(ds_app_ids)
        await self.delete_links(ds_app_ids)

    async def log_ds_app_ids(self, ds_app_ids: list[int]):
        await self.add_task_log(f"Deleting agencies with the following ds_app_ids: {ds_app_ids}")

    async def get_inputs(self) -> list[int]:
        return await self.adb_client.run_query_builder(
            DSAppSyncAgenciesDeleteGetQueryBuilder()
        )

    async def make_request(
        self,
        ds_app_ids: list[int]
    ) -> None:
        await self.pdap_client.run_request_builder(
            DeleteAgenciesRequestBuilder(ds_app_ids)
        )

    async def delete_flags(
        self,
        ds_app_ids: list[int]
    ) -> None:
        await self.run_query_builder(
            DSAppSyncAgenciesDeleteRemoveFlagsQueryBuilder(
                ds_agency_ids=ds_app_ids
            )
        )

    async def delete_links(
        self,
        ds_app_ids: list[int]
    ) -> None:
        await self.run_query_builder(
            DSAppSyncAgenciesDeleteRemoveLinksQueryBuilder(
                ds_agency_ids=ds_app_ids
            )
        )