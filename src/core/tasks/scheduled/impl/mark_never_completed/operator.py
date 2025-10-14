from src.core.tasks.scheduled.impl.mark_never_completed.query import MarkTaskNeverCompletedQueryBuilder
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.enums import TaskType


class MarkTaskNeverCompletedOperator(ScheduledTaskOperatorBase):

    @property
    def task_type(self) -> TaskType:
        return TaskType.MARK_TASK_NEVER_COMPLETED

    async def inner_task_logic(self) -> None:
        await self.adb_client.run_query_builder(
            MarkTaskNeverCompletedQueryBuilder()
        )