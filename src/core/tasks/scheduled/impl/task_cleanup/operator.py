from src.core.tasks.scheduled.impl.task_cleanup.query import TaskCleanupQueryBuilder
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.enums import TaskType


class TaskCleanupOperator(ScheduledTaskOperatorBase):

    @property
    def task_type(self) -> TaskType:
        return TaskType.TASK_CLEANUP

    async def inner_task_logic(self) -> None:
        await self.adb_client.run_query_builder(
            TaskCleanupQueryBuilder()
        )