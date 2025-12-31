from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from src.api.endpoints.task.by_id.dto import TaskInfo
from src.collectors.enums import URLStatus
from src.db.enums import TaskType
from src.db.models.impl.task.core import Task
from src.db.models.impl.task.enums import TaskStatus
from src.db.models.impl.url.core.pydantic.info import URLInfo
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.error_info.pydantic import URLErrorInfoPydantic
from src.db.queries.base.builder import QueryBuilderBase


class GetTaskInfoQueryBuilder(QueryBuilderBase):

    def __init__(self, task_id: int):
        super().__init__()
        self.task_id = task_id

    async def run(self, session: AsyncSession) -> TaskInfo:
        # Get Task
        result = await session.execute(
            select(Task)
            .where(Task.id == self.task_id)
            .options(
                selectinload(Task.urls)
                .selectinload(URL.batch),
                selectinload(Task.url_errors),
                selectinload(Task.errors)
            )
        )
        task = result.scalars().first()
        error = task.errors[0].error if len(task.errors) > 0 else None
        # Get error info if any
        # Get URLs
        # TODO: Revise to include URL Status from URL Web metadata
        urls = task.urls
        url_infos = []
        for url in urls:
            url_info = URLInfo(
                id=url.id,
                batch_id=url.batch.id,
                url=url.url,
                collector_metadata=url.collector_metadata,
                updated_at=url.updated_at
            )
            url_infos.append(url_info)

        errored_urls = []
        for url in task.url_errors:
            url_error_info = URLErrorInfoPydantic(
                task_id=url.task_id,
                url_id=url.url_id,
                error=url.error,
                updated_at=url.created_at
            )
            errored_urls.append(url_error_info)
        return TaskInfo(
            task_type=TaskType(task.task_type),
            task_status=TaskStatus(task.task_status),
            error_info=error,
            updated_at=task.updated_at,
            urls=url_infos,
            url_errors=errored_urls
        )