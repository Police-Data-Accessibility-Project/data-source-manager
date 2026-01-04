from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.update.queries.get import \
    DSAppSyncMetaURLsUpdateGetQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.update.queries.prereq import \
    DSAppSyncMetaURLsUpdatePrerequisitesQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.update.queries.update_links import \
    DSAppSyncMetaURLsUpdateAlterLinksQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.templates.operator import DSSyncTaskOperatorBase
from src.db.enums import TaskType
from src.external.pdap.impl.sync.meta_urls.update.core import UpdateMetaURLsRequestBuilder
from src.external.pdap.impl.sync.meta_urls.update.request import UpdateMetaURLsOuterRequest


class DSAppSyncMetaURLsUpdateTaskOperator(
    DSSyncTaskOperatorBase
):

    @property
    def task_type(self) -> TaskType:
        return TaskType.SYNC_META_URLS_UPDATE

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.run_query_builder(
            DSAppSyncMetaURLsUpdatePrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:
        request: UpdateMetaURLsOuterRequest = await self.get_inputs()
        ds_app_ids: list[int] = [
            meta_url.app_id
            for meta_url in request.meta_urls
        ]
        await self.log_ds_app_ids(ds_app_ids)
        await self.make_request(request)
        await self.update_links(ds_app_ids)

    async def log_ds_app_ids(self, ds_app_ids: list[int]):
        await self.add_task_log(f"Updating meta urls with the following ds_app_ids: {ds_app_ids}")

    async def get_inputs(self) -> UpdateMetaURLsOuterRequest:
        return await self.adb_client.run_query_builder(
            DSAppSyncMetaURLsUpdateGetQueryBuilder()
        )

    async def make_request(
        self,
        request: UpdateMetaURLsOuterRequest
    ):
        await self.pdap_client.run_request_builder(
            UpdateMetaURLsRequestBuilder(request)
        )

    async def update_links(
        self,
        ds_app_ids: list[int]
    ) -> None:
        await self.adb_client.run_query_builder(
            DSAppSyncMetaURLsUpdateAlterLinksQueryBuilder(
                ds_meta_url_ids=ds_app_ids
            )
        )