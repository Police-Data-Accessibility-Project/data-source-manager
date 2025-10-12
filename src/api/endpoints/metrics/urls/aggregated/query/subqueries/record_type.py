from typing import Sequence

from sqlalchemy import select, func, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.enums import RecordType
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from src.db.queries.base.builder import QueryBuilderBase


class GetURLRecordTypeCountQueryBuilder(QueryBuilderBase):

    async def run(
        self,
        session: AsyncSession
    ) -> dict[RecordType, int]:
        query = (
            select(
                URLRecordType.record_type,
                func.count(URLRecordType.url_id).label("count")
            )
            .group_by(
                URLRecordType.record_type
            )
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)

        return {
            mapping["record_type"]: mapping["count"]
            for mapping in mappings
        }