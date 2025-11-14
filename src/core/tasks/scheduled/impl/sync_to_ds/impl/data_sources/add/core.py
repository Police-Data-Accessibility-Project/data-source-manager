from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.add.queries.add_links import \
    DSAppSyncDataSourcesAddInsertLinksQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.add.queries.get import \
    DSAppSyncDataSourcesAddGetQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.add.queries.prereq import \
    DSAppSyncDataSourcesAddPrerequisitesQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.templates.operator import DSSyncTaskOperatorBase
from src.db.enums import TaskType
from src.external.pdap.impl.sync.data_sources.add.core import AddDataSourcesRequestBuilder
from src.external.pdap.impl.sync.data_sources.add.request import AddDataSourcesOuterRequest
from src.external.pdap.impl.sync.shared.models.add.response import DSAppSyncAddResponseInnerModel


class DSAppSyncDataSourcesAddTaskOperator(
    DSSyncTaskOperatorBase
):

    @property
    def task_type(self) -> TaskType:
        return TaskType.SYNC_DATA_SOURCES_ADD

    async def meets_task_prerequisites(self) -> bool:
        return await self.run_query_builder(
            DSAppSyncDataSourcesAddPrerequisitesQueryBuilder()
        )


    async def inner_task_logic(self) -> None:
        request: AddDataSourcesOuterRequest = await self.get_request_input()
        responses: list[DSAppSyncAddResponseInnerModel] = await self.make_request(request)
        await self.insert_ds_app_links(responses)


    async def get_request_input(self) -> AddDataSourcesOuterRequest:
        return await self.run_query_builder(
            DSAppSyncDataSourcesAddGetQueryBuilder()
        )

    async def make_request(
        self,
        request: AddDataSourcesOuterRequest
    ) -> list[DSAppSyncAddResponseInnerModel]:
        return await self.pdap_client.run_request_builder(
            AddDataSourcesRequestBuilder(request)
        )

    async def insert_ds_app_links(
        self,
        responses: list[DSAppSyncAddResponseInnerModel]
    ) -> None:
        await self.run_query_builder(
            DSAppSyncDataSourcesAddInsertLinksQueryBuilder(responses)
        )
