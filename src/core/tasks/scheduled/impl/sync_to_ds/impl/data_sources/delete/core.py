from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.delete.queries.delete_flags import \
    DSAppSyncDataSourcesDeleteRemoveFlagsQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.delete.queries.delete_links import \
    DSAppSyncDataSourcesDeleteRemoveLinksQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.delete.queries.get import \
    DSAppSyncDataSourcesDeleteGetQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.delete.queries.prereq import \
    DSAppSyncDataSourcesDeletePrerequisitesQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.templates.operator import DSSyncTaskOperatorBase
from src.db.enums import TaskType
from src.external.pdap.impl.sync.data_sources.delete.core import DeleteDataSourcesRequestBuilder


class DSAppSyncDataSourcesDeleteTaskOperator(
    DSSyncTaskOperatorBase
):

    @property
    def task_type(self) -> TaskType:
        return TaskType.SYNC_DATA_SOURCES_DELETE

    async def meets_task_prerequisites(self) -> bool:
        return await self.run_query_builder(
            DSAppSyncDataSourcesDeletePrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:
        ds_app_ids: list[int] = await self.get_inputs()
        await self.make_request(ds_app_ids)
        await self.delete_flags(ds_app_ids)
        await self.delete_links(ds_app_ids)

    async def get_inputs(self) -> list[int]:
        return await self.run_query_builder(
            DSAppSyncDataSourcesDeleteGetQueryBuilder()
        )

    async def make_request(
        self,
        ds_app_ids: list[int]
    ) -> None:
        await self.pdap_client.run_request_builder(
            DeleteDataSourcesRequestBuilder(ds_app_ids)
        )

    async def delete_flags(
        self,
        ds_app_ids: list[int]
    ) -> None:
        await self.run_query_builder(
            DSAppSyncDataSourcesDeleteRemoveFlagsQueryBuilder(
                ds_data_source_ids=ds_app_ids
            )
        )

    async def delete_links(
        self,
        ds_app_ids: list[int]
    ) -> None:
        await self.run_query_builder(
            DSAppSyncDataSourcesDeleteRemoveLinksQueryBuilder(
                ds_data_source_ids=ds_app_ids
            )
        )