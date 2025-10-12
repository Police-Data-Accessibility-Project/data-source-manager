from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.enums import TaskType


class RefreshMaterializedViewsOperator(ScheduledTaskOperatorBase):

    @property
    def task_type(self) -> TaskType:
        return TaskType.REFRESH_MATERIALIZED_VIEWS

    async def inner_task_logic(self) -> None:
        await self.adb_client.refresh_materialized_views()