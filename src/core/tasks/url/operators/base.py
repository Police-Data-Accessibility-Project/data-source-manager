from src.core.tasks.base.operator import TaskOperatorBase
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.mixins.link_urls import LinkURLsMixin
from src.core.tasks.mixins.prereq import HasPrerequisitesMixin
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.db.client.async_ import AsyncDatabaseClient


class URLTaskOperatorBase(
    TaskOperatorBase,
    LinkURLsMixin,
    HasPrerequisitesMixin,
):

    def __init__(self, adb_client: AsyncDatabaseClient):
        super().__init__(adb_client)

    async def conclude_task(self):
        if not self.urls_linked:
            raise Exception("Task has not been linked to any URLs")
        return await self.run_info(
            outcome=TaskOperatorOutcome.SUCCESS,
            message="Task completed successfully"
        )

    async def run_info(
        self,
        outcome: TaskOperatorOutcome,
        message: str
    ) -> TaskOperatorRunInfo:
        return TaskOperatorRunInfo(
            task_id=self.task_id,
            task_type=self.task_type,
            outcome=outcome,
            message=message
        )
