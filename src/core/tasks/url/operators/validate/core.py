from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.validate.queries.get.core import GetURLsForAutoValidationQueryBuilder
from src.core.tasks.url.operators.validate.queries.get.models.response import GetURLsForAutoValidationResponse
from src.core.tasks.url.operators.validate.queries.insert import InsertURLAutoValidationsQueryBuilder
from src.core.tasks.url.operators.validate.queries.prereq.core import AutoValidatePrerequisitesQueryBuilder
from src.db.enums import TaskType


class AutoValidateURLTaskOperator(URLTaskOperatorBase):

    @property
    def task_type(self) -> TaskType:
        return TaskType.AUTO_VALIDATE

    async def meets_task_prerequisites(self) -> bool:
        return await self.adb_client.run_query_builder(
            AutoValidatePrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:
        # Get URLs for auto validation
        responses: list[GetURLsForAutoValidationResponse] = await self.adb_client.run_query_builder(
            GetURLsForAutoValidationQueryBuilder()
        )
        url_ids: list[int] = [response.url_id for response in responses]
        await self.link_urls_to_task(url_ids)

        await self.adb_client.run_query_builder(
            InsertURLAutoValidationsQueryBuilder(responses)
        )
