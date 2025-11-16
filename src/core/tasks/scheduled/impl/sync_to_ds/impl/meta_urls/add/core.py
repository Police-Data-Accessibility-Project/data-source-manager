from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.add.queries.add_links import \
    DSAppSyncMetaURLsAddInsertLinksQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.add.queries.get import DSAppSyncMetaURLsAddGetQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.add.queries.prereq import \
    DSAppSyncMetaURLsAddPrerequisitesQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.templates.operator import DSSyncTaskOperatorBase
from src.db.enums import TaskType
from src.external.pdap.impl.sync.meta_urls.add.core import AddMetaURLsRequestBuilder
from src.external.pdap.impl.sync.meta_urls.add.request import AddMetaURLsOuterRequest, AddMetaURLsInnerRequest
from src.external.pdap.impl.sync.shared.models.add.response import DSAppSyncAddResponseInnerModel


class DSAppSyncMetaURLsAddTaskOperator(
    DSSyncTaskOperatorBase
):

    @property
    def task_type(self) -> TaskType:
        return TaskType.SYNC_META_URLS_ADD

    async def meets_task_prerequisites(self) -> bool:
        return await self.run_query_builder(
            DSAppSyncMetaURLsAddPrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:
        request: AddMetaURLsOuterRequest = await self.get_request_input()
        await self.log_db_ids(request.meta_urls)
        responses: list[DSAppSyncAddResponseInnerModel] = await self.make_request(request)
        await self.insert_ds_app_links(responses)

    async def log_db_ids(self, meta_urls: list[AddMetaURLsInnerRequest]):
        db_ids: list[int] = [m.request_id for m in meta_urls]
        await self.add_task_log(f"Adding meta urls with the following db_ids: {db_ids}")

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
