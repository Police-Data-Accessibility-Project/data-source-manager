from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.submit_meta_urls.queries.get import GetMetaURLsForSubmissionQueryBuilder
from src.core.tasks.url.operators.submit_meta_urls.queries.prereq import \
    MeetsMetaURLSSubmissionPrerequisitesQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url.mapping import URLMapping
from src.db.enums import TaskType
from src.db.models.impl.url.ds_meta_url.pydantic import URLDSMetaURLPydantic
from src.db.models.impl.url.error_info.pydantic import URLErrorInfoPydantic
from src.external.pdap.client import PDAPClient
from src.external.pdap.impl.meta_urls.enums import SubmitMetaURLsStatus
from src.external.pdap.impl.meta_urls.request import SubmitMetaURLsRequest
from src.external.pdap.impl.meta_urls.response import SubmitMetaURLsResponse
from src.util.url_mapper import URLMapper


class SubmitMetaURLsTaskOperator(URLTaskOperatorBase):

    def __init__(
        self,
        adb_client: AsyncDatabaseClient,
        pdap_client: PDAPClient
    ):
        super().__init__(adb_client)
        self.pdap_client = pdap_client

    @property
    def task_type(self) -> TaskType:
        return TaskType.SUBMIT_META_URLS

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.run_query_builder(
            MeetsMetaURLSSubmissionPrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:
        requests: list[SubmitMetaURLsRequest] = await self.adb_client.run_query_builder(
            GetMetaURLsForSubmissionQueryBuilder()
        )

        url_mappings: list[URLMapping] = [
            URLMapping(
                url=request.url,
                url_id=request.url_id,
            )
            for request in requests
        ]

        mapper = URLMapper(url_mappings)

        await self.link_urls_to_task(mapper.get_all_ids())

        responses: list[SubmitMetaURLsResponse] = \
            await self.pdap_client.submit_meta_urls(requests)

        errors: list[URLErrorInfoPydantic] = []
        inserts: list[URLDSMetaURLPydantic] = []

        for response in responses:
            url_id: int = mapper.get_id(response.url)
            if response.status == SubmitMetaURLsStatus.SUCCESS:
                inserts.append(
                    URLDSMetaURLPydantic(
                        url_id=url_id,
                        agency_id=response.agency_id,
                        ds_meta_url_id=response.meta_url_id
                    )
                )
            else:
                errors.append(
                    URLErrorInfoPydantic(
                        url_id=url_id,
                        task_id=self.task_id,
                        error=response.error,
                    )
                )

            await self.adb_client.bulk_insert(errors)
            await self.adb_client.bulk_insert(inserts)
