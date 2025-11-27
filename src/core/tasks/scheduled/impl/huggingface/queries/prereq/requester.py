from datetime import datetime
from operator import or_

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from src.collectors.enums import URLStatus
from src.core.tasks.scheduled.impl.huggingface.queries.cte import HuggingfacePrereqCTEContainer
from src.db.enums import TaskType
from src.db.helpers.query import not_exists_url, no_url_task_error, exists_url
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.state.huggingface import HuggingFaceUploadState
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.core.sqlalchemy import URL


class CheckValidURLsUpdatedRequester:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def latest_upload(self) -> datetime:
        query = (
            select(
                HuggingFaceUploadState.last_upload_at
            )
        )
        return await sh.scalar(
            session=self.session,
            query=query
        )

    async def has_valid_urls(self, last_upload_at: datetime | None) -> bool:
        cte = HuggingfacePrereqCTEContainer()
        query = (
            select(
                cte.url_id
            )
        )
        if last_upload_at is not None:
            query = query.where(cte.updated_at > last_upload_at)
        query = query.limit(1)
        result = await sh.one_or_none(
            session=self.session,
            query=query
        )
        return result is not None