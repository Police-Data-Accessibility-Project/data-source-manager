from datetime import timedelta, datetime
from typing import Any

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.task.core import Task
from src.db.queries.base.builder import QueryBuilderBase


class TaskCleanupQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> Any:
        one_week_ago: datetime = datetime.now() - timedelta(days=7)

        statement = (
            delete(Task)
            .where(
                Task.updated_at < one_week_ago
            )
        )

        await session.execute(statement)