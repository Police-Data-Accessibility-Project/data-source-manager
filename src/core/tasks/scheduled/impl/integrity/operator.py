from src.core.tasks.mixins.prereq import HasPrerequisitesMixin
from src.core.tasks.scheduled.impl.integrity.exceptions import IntegrityMonitorTaskException
from src.core.tasks.scheduled.impl.integrity.queries.get import GetIntegrityTaskDataQueryBuilder
from src.core.tasks.scheduled.impl.integrity.queries.prereq import GetIntegrityTaskPrerequisitesQueryBuilder
from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.enums import TaskType


class IntegrityMonitorTaskOperator(
    ScheduledTaskOperatorBase,
    HasPrerequisitesMixin
):

    @property
    def task_type(self) -> TaskType:
        return TaskType.INTEGRITY_MONITOR

    async def meets_task_prerequisites(self) -> bool:
        return await self.run_query_builder(
            query_builder=GetIntegrityTaskPrerequisitesQueryBuilder()
        )

    async def inner_task_logic(self) -> None:
        failing_views: list[str] = await self.run_query_builder(
            query_builder=GetIntegrityTaskDataQueryBuilder()
        )
        raise IntegrityMonitorTaskException(
            f"Integrity Monitor Task failed for the following views {failing_views}",
        )

