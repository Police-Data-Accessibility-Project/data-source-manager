from datetime import timedelta, datetime
from typing import Any

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import BatchStatus
from src.db.enums import TaskType
from src.db.models.impl.task.core import Task
from src.db.models.impl.task.enums import TaskStatus
from src.db.queries.base.builder import QueryBuilderBase


class MarkTaskNeverCompletedQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> Any:
        statement = (
            update(
                Task
            ).values(
                task_status=TaskStatus.NEVER_COMPLETED.value
            ).
            where(
                Task.task_status == TaskStatus.IN_PROCESS,
                Task.updated_at < datetime.now() - timedelta(hours=1)
            )
        )
        await session.execute(statement)