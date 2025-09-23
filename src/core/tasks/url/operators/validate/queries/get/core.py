from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.agency import AgencyValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.location import LocationValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.record_type import \
    RecordTypeValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.url_type import URLTypeValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.helper import add_where_condition
from src.core.tasks.url.operators.validate.queries.get.models.response import GetURLsForAutoValidationResponse
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh

class GetURLsForAutoValidationQueryBuilder(QueryBuilderBase):


    async def run(self, session: AsyncSession) -> list[GetURLsForAutoValidationResponse]:
        agency = AgencyValidationCTEContainer()
        location = LocationValidationCTEContainer()
        url_type = URLTypeValidationCTEContainer()
        record_type = RecordTypeValidationCTEContainer()

        query = (
            select(
                URL.id.label("url_id"),
                location.location_id,
                agency.agency_id,
                url_type.url_type,
                record_type.record_type,
            )
            .outerjoin(
                agency.query,
                URL.id == agency.url_id,
            )
            .outerjoin(
                location.query,
                URL.id == location.url_id,
            )
            .outerjoin(
                url_type.query,
                URL.id == url_type.url_id,
            )
            .outerjoin(
                record_type.query,
                URL.id == record_type.url_id,
            )
        )
        query = add_where_condition(
            query,
            agency=agency,
            location=location,
            url_type=url_type,
            record_type=record_type,
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        return [
            GetURLsForAutoValidationResponse(**mapping) for mapping in mappings
        ]