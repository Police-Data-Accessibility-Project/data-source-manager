from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import FailedValidationException
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.agency import AgencyValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.location import LocationValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.name import NameValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.record_type import \
    RecordTypeValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.impl.url_type import URLTypeValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.get.models.response import GetURLsForAutoValidationResponse
from src.core.tasks.url.operators.validate.queries.helper import add_where_condition
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetURLsForAutoValidationQueryBuilder(QueryBuilderBase):


    async def run(self, session: AsyncSession) -> list[GetURLsForAutoValidationResponse]:
        agency = AgencyValidationCTEContainer()
        location = LocationValidationCTEContainer()
        url_type = URLTypeValidationCTEContainer()
        record_type = RecordTypeValidationCTEContainer()
        name = NameValidationCTEContainer()

        query = (
            select(
                URL.id.label("url_id"),
                location.location_id,
                agency.agency_id,
                url_type.url_type,
                record_type.record_type,
                name.name,
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
            .outerjoin(
                name.query,
                URL.id == name.url_id,
            )
        )
        query = add_where_condition(
            query,
            agency=agency,
            location=location,
            url_type=url_type,
            record_type=record_type,
            name=name,
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        responses: list[GetURLsForAutoValidationResponse] = []
        for mapping in mappings:
            try:
                response = GetURLsForAutoValidationResponse(**mapping)
                responses.append(response)
            except FailedValidationException as e:
                raise FailedValidationException(
                    f"Failed to validate URL {mapping['url_id']}") from e
        return responses
