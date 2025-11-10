from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.add.queries.add_links import \
    DSAppSyncAgenciesAddInsertLinksQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.add.queries.get import DSAppSyncAgenciesAddGetQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.add.queries.prereq import \
    DSAppSyncAgenciesAddPrerequisitesQueryBuilder
from src.core.tasks.scheduled.impl.sync_to_ds.templates.operator import DSSyncTaskOperatorBase
from src.external.pdap.impl.sync.agencies.add.core import AddAgenciesRequestBuilder
from src.external.pdap.impl.sync.agencies.add.request import AddAgenciesOuterRequest
from src.external.pdap.impl.sync.shared.models.add.response import DSAppSyncAddResponseInnerModel


class DSAppSyncAgenciesAddTaskOperator(
    DSSyncTaskOperatorBase
):

    async def meets_task_prerequisites(self) -> bool:
        return await self.run_query_builder(
            DSAppSyncAgenciesAddPrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:
        request: AddAgenciesOuterRequest = await self.get_request_input()
        responses: list[DSAppSyncAddResponseInnerModel] = await self.make_request(request)
        await self.insert_ds_app_links(responses)

    async def get_request_input(self) -> AddAgenciesOuterRequest:
        return await self.run_query_builder(
            DSAppSyncAgenciesAddGetQueryBuilder()
        )

    async def make_request(
        self,
        request: AddAgenciesOuterRequest
    ) -> list[DSAppSyncAddResponseInnerModel]:
        return await self.pdap_client.run_request_builder(
            AddAgenciesRequestBuilder(request)
        )

    async def insert_ds_app_links(
        self,
        responses: list[DSAppSyncAddResponseInnerModel]
    ) -> None:
        await self.run_query_builder(
            DSAppSyncAgenciesAddInsertLinksQueryBuilder(responses)
        )
