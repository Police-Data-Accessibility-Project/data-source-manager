from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import RecordType
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from src.db.queries.base.builder import QueryBuilderBase


class UpdateRecordTypeQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int,
        record_type: RecordType
    ):
        super().__init__()
        self.url_id = url_id
        self.record_type = record_type

    async def run(self, session: AsyncSession) -> None:
        statement = (
            update(
                URLRecordType
            )
            .where(
                URLRecordType.url_id == self.url_id
            )
            .values(
                record_type=self.record_type
            )
        )
        await session.execute(statement)