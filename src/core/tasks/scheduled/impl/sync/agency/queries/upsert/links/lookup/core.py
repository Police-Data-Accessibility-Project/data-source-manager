from collections import defaultdict
from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.response import AgencyURLMappings
from src.db.models.impl.flag.url_validated.enums import URLValidatedType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class LookupMetaURLAgencyLinksQueryBuilder(QueryBuilderBase):
    """Given a set of Agency IDs, return all Meta URL agency links."""

    def __init__(self, agency_ids: list[int]):
        super().__init__()
        self._agency_ids = agency_ids

    async def run(self, session: AsyncSession) -> list[AgencyURLMappings]:
        query = (
            select(
                LinkURLAgency.url_id,
                LinkURLAgency.agency_id,
            )
            .outerjoin(
                FlagURLValidated,
                FlagURLValidated.url_id == LinkURLAgency.url_id,
            )
            .where(
                LinkURLAgency.agency_id.in_(self._agency_ids),
                FlagURLValidated.type == URLValidatedType.META_URL
            )
        )
        db_mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)

        agency_id_to_url_ids: dict[int, list[int]] = defaultdict(list)
        for mapping in db_mappings:
            agency_id: int = mapping["agency_id"]
            url_id: int = mapping["url_id"]
            agency_id_to_url_ids[agency_id].append(url_id)

        result_mappings: list[AgencyURLMappings] = []
        for agency_id in agency_id_to_url_ids.keys():
            url_ids: list[int] = agency_id_to_url_ids[agency_id]
            result_mapping = AgencyURLMappings(
                agency_id=agency_id,
                url_ids=url_ids,
            )
            result_mappings.append(result_mapping)

        return result_mappings