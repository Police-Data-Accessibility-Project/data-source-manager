from src.core.tasks.scheduled.impl.update_url_status.query import UpdateURLStatusQueryBuilder
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.enums import TaskType


class UpdateURLStatusOperator(ScheduledTaskOperatorBase):

    @property
    def task_type(self) -> TaskType:
        return TaskType.UPDATE_URL_STATUS

    async def inner_task_logic(self) -> None:
        await self.adb_client.run_query_builder(
            UpdateURLStatusQueryBuilder()
        )