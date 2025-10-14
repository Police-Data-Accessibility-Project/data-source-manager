from datetime import timedelta, datetime

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override, final

from src.util.url import clean_url
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from src.db.helpers.session import session_helper as sh
from src.db.queries.base.builder import QueryBuilderBase


@final
class GetURLsWithoutProbeQueryBuilder(QueryBuilderBase):

    @override
    async def run(self, session: AsyncSession) -> list[URLMapping]:
        query = (
            select(
                URL.id.label("url_id"),
                URL.full_url.label("url")
            )
            .outerjoin(
                URLWebMetadata,
                URL.id == URLWebMetadata.url_id
            )
            .where(
                or_(
                    URLWebMetadata.id.is_(None),
                    URLWebMetadata.updated_at < datetime.now() - timedelta(days=30)
                )
            )
            .limit(500)
        )
        db_mappings = await sh.mappings(session, query=query)
        return [
            URLMapping(
                url_id=mapping["url_id"],
                url=clean_url(mapping["url"])
            ) for mapping in db_mappings
        ]