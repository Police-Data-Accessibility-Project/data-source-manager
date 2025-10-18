from datetime import timedelta, datetime

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override, final

from src.db.dtos.url.mapping_.full import FullURLMapping
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from src.db.queries.base.builder import QueryBuilderBase
from src.util.models.full_url import FullURL


@final
class GetURLsWithoutProbeQueryBuilder(QueryBuilderBase):

    @override
    async def run(self, session: AsyncSession) -> list[FullURLMapping]:
        query = (
            select(
                URL.id.label("url_id"),
                URL.full_url
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
            FullURLMapping(
                url_id=mapping["url_id"],
                full_url=FullURL(mapping["full_url"])
            ) for mapping in db_mappings
        ]