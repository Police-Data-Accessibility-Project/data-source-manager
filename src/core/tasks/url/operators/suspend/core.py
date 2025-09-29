from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.suspend.queries.get.query import GetURLsForSuspensionQueryBuilder
from src.core.tasks.url.operators.suspend.queries.get.response import GetURLsForSuspensionResponse
from src.core.tasks.url.operators.suspend.queries.insert import InsertURLSuspensionsQueryBuilder
from src.core.tasks.url.operators.suspend.queries.prereq import GetURLsForSuspensionPrerequisitesQueryBuilder
from src.db.enums import TaskType


class SuspendURLTaskOperator(URLTaskOperatorBase):

    @property
    def task_type(self) -> TaskType:
        return TaskType.SUSPEND_URLS

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.run_query_builder(
            GetURLsForSuspensionPrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:
        # Get URLs for auto validation
        responses: list[GetURLsForSuspensionResponse] = await self.adb_client.run_query_builder(
            GetURLsForSuspensionQueryBuilder()
        )
        url_ids: list[int] = [response.url_id for response in responses]
        await self.link_urls_to_task(url_ids)

        await self.adb_client.run_query_builder(
            InsertURLSuspensionsQueryBuilder(responses)
        )
