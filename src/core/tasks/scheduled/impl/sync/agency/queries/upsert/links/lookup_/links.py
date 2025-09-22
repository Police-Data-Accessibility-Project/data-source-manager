from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.helpers.session import session_helper as sh
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.url_agency.pydantic import LinkURLAgencyPydantic
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class LookupMetaURLLinksQueryBuilder(QueryBuilderBase):

    def __init__(self, agency_ids: list[int]):
        super().__init__()
        self.agency_ids: list[int] = agency_ids

    async def run(self, session: AsyncSession) -> list[LinkURLAgencyPydantic]:

        query = (
            select(
                LinkURLAgency.url_id,
                LinkURLAgency.agency_id
            )
            .join(
                URL,
                LinkURLAgency.url_id == URL.id,
            )
            .join(
                FlagURLValidated,
                FlagURLValidated.url_id == URL.id,
            )
            .where(
                FlagURLValidated.type == URLType.META_URL,
                LinkURLAgency.agency_id.in_(self.agency_ids),
            )
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        links: list[LinkURLAgencyPydantic] = [
            LinkURLAgencyPydantic(**mapping) for mapping in mappings
        ]
        return links