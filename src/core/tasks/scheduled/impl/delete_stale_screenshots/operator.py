from src.core.tasks.scheduled.impl.delete_stale_screenshots.query import DeleteStaleScreenshotsQueryBuilder
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.enums import TaskType


class DeleteStaleScreenshotsTaskOperator(ScheduledTaskOperatorBase):

    @property
    def task_type(self) -> TaskType:
        return TaskType.DELETE_STALE_SCREENSHOTS

    async def inner_task_logic(self) -> None:
        await self.adb_client.run_query_builder(
            DeleteStaleScreenshotsQueryBuilder()
        )