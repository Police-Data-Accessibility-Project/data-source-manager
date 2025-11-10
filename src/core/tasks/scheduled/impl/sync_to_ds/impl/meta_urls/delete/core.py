from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.delete.queries.delete_flags import \
    DSAppSyncMetaURLsDeleteRemoveFlagsQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.delete.queries.delete_links import \
    DSAppSyncMetaURLsDeleteRemoveLinksQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.delete.queries.get import \
    DSAppSyncMetaURLsDeleteGetQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.delete.queries.prereq import \
    DSAppSyncMetaURLsDeletePrerequisitesQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.templates.operator import DSSyncTaskOperatorBase
from src.external.pdap.impl.sync.meta_urls.delete.core import DeleteMetaURLsRequestBuilder


class DSAppSyncMetaURLsDeleteTaskOperator(
    DSSyncTaskOperatorBase
):

    async def meets_task_prerequisites(self) -> bool:
        return await self.run_query_builder(
            DSAppSyncMetaURLsDeletePrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:
        ds_app_ids: list[int] = await self.get_inputs()
        await self.make_request(ds_app_ids)
        await self.delete_flags(ds_app_ids)
        await self.delete_links(ds_app_ids)

    async def get_inputs(self) -> list[int]:
        return await self.run_query_builder(
            DSAppSyncMetaURLsDeleteGetQueryBuilder()
        )

    async def make_request(
        self,
        ds_app_ids: list[int]
    ) -> None:
        await self.pdap_client.run_request_builder(
            DeleteMetaURLsRequestBuilder(ds_app_ids)
        )

    async def delete_flags(
        self,
        ds_app_ids: list[int]
    ) -> None:
        await self.run_query_builder(
            DSAppSyncMetaURLsDeleteRemoveFlagsQueryBuilder(
                ds_meta_url_ids=ds_app_ids
            )
        )

    async def delete_links(
        self,
        ds_app_ids: list[int]
    ) -> None:
        await self.run_query_builder(
            DSAppSyncMetaURLsDeleteRemoveLinksQueryBuilder(
                ds_meta_url_ids=ds_app_ids
            )
        )