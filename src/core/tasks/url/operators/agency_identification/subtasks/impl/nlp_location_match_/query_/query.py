from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.query_.response import \
    GetAgenciesLinkedToAnnotatedLocationsResponse
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.location.auto.suggestion.sqlalchemy import LocationIDSubtaskSuggestion
from src.db.queries.base.builder import QueryBuilderBase


class GetAgenciesLinkedToAnnotatedLocationsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[GetAgenciesLinkedToAnnotatedLocationsResponse]:

    query = (
        select(
            URL.id,
            LocationIDSubtaskSuggestion.location_id,
            LocationIDSubtaskSuggestion.confidence,
            Agency.id
        )
        .outerjoin(

        )
    )