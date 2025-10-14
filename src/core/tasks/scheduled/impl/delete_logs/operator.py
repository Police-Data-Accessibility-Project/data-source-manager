import datetime

from sqlalchemy import delete

from src.core.tasks.scheduled.templates.operator import ScheduledTaskOperatorBase
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.db.models.impl.log.sqlalchemy import Log


class DeleteOldLogsTaskOperator(ScheduledTaskOperatorBase):

    @property
    def task_type(self) -> TaskType:
        return TaskType.DELETE_OLD_LOGS

    async def inner_task_logic(self) -> None:
        statement = delete(Log).where(
            Log.created_at < datetime.datetime.now() - datetime.timedelta(days=7)
        )
        await self.adb_client.execute(statement)