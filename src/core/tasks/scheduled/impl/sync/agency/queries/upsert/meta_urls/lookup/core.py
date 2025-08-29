from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.lookup.response import MetaURLLookupResponse
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class LookupMetaURLsQueryBuilder(QueryBuilderBase):
    """Lookup whether URLs exist in DB and are validated as meta URLs"""

    def __init__(self, urls: list[str]):
        super().__init__()
        self.urls = urls

    async def run(self, session: AsyncSession) -> list[MetaURLLookupResponse]:
        query = (
            select(
                URL.id,
                URL.url,
                URL.record_type,
                FlagURLValidated.type
            )
            .where(
                URL.url.in_(self.urls)
            )
            .join(
                FlagURLValidated,
                FlagURLValidated.url_id == URL.id,
                isouter=True
            )
        )
        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)

        return [
            MetaURLLookupResponse(
                url=mapping["url"],
                url_id=mapping["id"],
                record_type=mapping["record_type"],
                validation_type=mapping["type"]
            ) for mapping in mappings
        ]