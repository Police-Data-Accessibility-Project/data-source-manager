from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.update.queries.get import \
    DSAppSyncDataSourcesUpdateGetQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.update.queries.prereq import \
    DSAppSyncDataSourcesUpdatePrerequisitesQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.update.queries.update_links import \
    DSAppSyncDataSourcesUpdateAlterLinksQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.templates.operator import DSSyncTaskOperatorBase
from src.db.enums import TaskType
from src.external.pdap.impl.sync.data_sources.update.core import UpdateDataSourcesRequestBuilder
from src.external.pdap.impl.sync.data_sources.update.request import UpdateDataSourcesOuterRequest


class DSAppSyncDataSourcesUpdateTaskOperator(
    DSSyncTaskOperatorBase
):

    @property
    def task_type(self) -> TaskType:
        return TaskType.SYNC_DATA_SOURCES_UPDATE

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.run_query_builder(
            DSAppSyncDataSourcesUpdatePrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:
        request: UpdateDataSourcesOuterRequest = await self.get_inputs()
        await self.make_request(request)
        ds_app_ids: list[int] = [
            ds.app_id
            for ds in request.data_sources
        ]
        await self.update_links(ds_app_ids)

    async def get_inputs(self) -> UpdateDataSourcesOuterRequest:
        return await self.adb_client.run_query_builder(
            DSAppSyncDataSourcesUpdateGetQueryBuilder()
        )

    async def make_request(
        self,
        request: UpdateDataSourcesOuterRequest
    ):
        await self.pdap_client.run_request_builder(
            UpdateDataSourcesRequestBuilder(request)
        )

    async def update_links(
        self,
        ds_app_ids: list[int]
    ) -> None:
        await self.adb_client.run_query_builder(
            DSAppSyncDataSourcesUpdateAlterLinksQueryBuilder(
                ds_data_source_ids=ds_app_ids
            )
        )