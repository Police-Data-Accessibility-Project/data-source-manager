from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.add.queries.add_links import \
    DSAppSyncMetaURLsAddInsertLinksQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.add.queries.get import DSAppSyncMetaURLsAddGetQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.add.queries.prereq import \
    DSAppSyncMetaURLsAddPrerequisitesQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.templates.operator import DSSyncTaskOperatorBase
from src.external.pdap.impl.sync.meta_urls.add.core import AddMetaURLsRequestBuilder
from src.external.pdap.impl.sync.meta_urls.add.request import AddMetaURLsOuterRequest
from src.external.pdap.impl.sync.shared.models.add.response import DSAppSyncAddResponseInnerModel


class DSAppSyncMetaURLsAddTaskOperator(
    DSSyncTaskOperatorBase
):

    async def meets_task_prerequisites(self) -> bool:
        return await self.run_query_builder(
            DSAppSyncMetaURLsAddPrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:
        request: AddMetaURLsOuterRequest = await self.get_request_input()
        responses: list[DSAppSyncAddResponseInnerModel] = await self.make_request(request)
        await self.insert_ds_app_links(responses)

    async def get_request_input(self) -> AddMetaURLsOuterRequest:
        return await self.run_query_builder(
            DSAppSyncMetaURLsAddGetQueryBuilder()
        )

    async def make_request(
        self,
        request: AddMetaURLsOuterRequest
    ) -> list[DSAppSyncAddResponseInnerModel]:
        return await self.pdap_client.run_request_builder(
            AddMetaURLsRequestBuilder(request)
        )

    async def insert_ds_app_links(
        self,
        responses: list[DSAppSyncAddResponseInnerModel]
    ) -> None:
        await self.run_query_builder(
            DSAppSyncMetaURLsAddInsertLinksQueryBuilder(responses)
        )
