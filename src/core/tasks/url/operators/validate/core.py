from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.core.tasks.url.operators.validate.queries.get.core import GetURLsForAutoValidationQueryBuilder
from src.core.tasks.url.operators.validate.queries.models.response import GetURLsForAutoValidationResponse
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
        # TODO (SM422): Implement


        # TODO: Sort URLs according to URL type, and apply appropriate validations

        # Link

        # Add Validation Objects (Flag and ValidationType)

        raise NotImplementedError