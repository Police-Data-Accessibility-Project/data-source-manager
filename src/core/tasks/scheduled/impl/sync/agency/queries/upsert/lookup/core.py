from typing import Sequence

from sqlalchemy import select, RowMapping, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.lookup.extract import \
    extract_agency_ids_from_agencies_sync_response
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.extract import extract_urls_from_agencies_sync_response
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.lookup.response import MetaURLLookupResponse
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


class LookupMetaURLsQueryBuilder(QueryBuilderBase):
    """Lookup whether URLs exist in DB and are validated as meta URLs"""

    def __init__(self, sync_responses: list[AgenciesSyncResponseInnerInfo]):
        super().__init__()
        self.urls: list[str] = extract_urls_from_agencies_sync_response(sync_responses)
        self.agency_ids: list[int] = extract_agency_ids_from_agencies_sync_response(sync_responses)

    async def run(self, session: AsyncSession) -> list[MetaURLLookupResponse]:
        agency_ids_label: str = "agency_ids"
        url_id_label: str = "url_id"

        cte = (
            select(
                URL.id.label(url_id_label),
                func.array_agg(
                    Agency.id,
                ).label(agency_ids_label)
            )
            .select_from(
                URL
            )
            .outerjoin(
                LinkURLAgency,
                LinkURLAgency.url_id == URL.id,
            )
            .where(
                or_(
                    URL.url.in_(self.urls),
                    LinkURLAgency.agency_id.in_(self.agency_ids)
                )
            )
            .group_by(
                URL.id,
            )
            .cte("urls_and_agencies")
        )

        query = (
            select(
                cte.c[url_id_label],
                cte.c[agency_ids_label],
                URL.url,
                URL.record_type,
                FlagURLValidated.type
            )
            .select_from(
                cte
            )
            .outerjoin(
                FlagURLValidated,
                FlagURLValidated.url_id == cte.c[url_id_label],
            )
            .outerjoin(
                URL,
                URL.id == cte.c[url_id_label],
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
                agency_ids=mapping[agency_ids_label],
            )
            extant_lookup_responses.append(response)

        urls_not_in_db = set(self.urls) - set(urls_in_db)
        non_extant_lookup_responses = [
            MetaURLLookupResponse(
                url=url,
                url_id=None,
                record_type=None,
                validation_type=None,
                agency_ids=[],
            ) for url in urls_not_in_db
        ]

        return extant_lookup_responses + non_extant_lookup_responses
