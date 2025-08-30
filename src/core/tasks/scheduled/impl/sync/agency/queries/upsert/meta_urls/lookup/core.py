from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.lookup.response import MetaURLLookupResponse
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class LookupMetaURLsQueryBuilder(QueryBuilderBase):
    """Lookup whether URLs exist in DB and are validated as meta URLs"""

    def __init__(self, urls: list[str]):
        super().__init__()
        self.urls: list[str] = urls

    async def run(self, session: AsyncSession) -> list[MetaURLLookupResponse]:
        url_id_label: str = "url_id"

        query = (
            select(
                URL.id.label(url_id_label),
                URL.url,
                URL.record_type,
                FlagURLValidated.type
            )
            .select_from(
                URL
            )
            .outerjoin(
                FlagURLValidated,
                FlagURLValidated.url_id == URL.id,
            )
            .where(
                URL.url.in_(self.urls)
            )
        )
        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)

        urls_in_db = set()
        extant_lookup_responses: list[MetaURLLookupResponse] = []
        for mapping in mappings:
            url = mapping["url"]
            urls_in_db.add(url)
            response = MetaURLLookupResponse(
                url=url,
                url_id=mapping[url_id_label],
                record_type=mapping["record_type"],
                validation_type=mapping["type"],
            )
            extant_lookup_responses.append(response)

        urls_not_in_db = set(self.urls) - set(urls_in_db)
        non_extant_lookup_responses = [
            MetaURLLookupResponse(
                url=url,
                url_id=None,
                record_type=None,
                validation_type=None,
            ) for url in urls_not_in_db
        ]

        return extant_lookup_responses + non_extant_lookup_responses
