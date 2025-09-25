from typing import Sequence

from sqlalchemy import select, func, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.search.agency.models.response import AgencySearchResponse
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.models.views.location_expanded import LocationExpandedView
from src.db.queries.base.builder import QueryBuilderBase


class SearchAgencyQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        location_id: int | None,
        query: str | None
    ):
        super().__init__()
        self.location_id = location_id
        self.query = query

    async def run(self, session: AsyncSession) -> list[AgencySearchResponse]:

        query = (
            select(
                Agency.agency_id,
                Agency.name.label("agency_name"),
                LocationExpandedView.display_name.label("location_display_name")
            )
            .join(
                LinkAgencyLocation,
                LinkAgencyLocation.agency_id == Agency.agency_id
            )
            .join(
                LocationExpandedView,
                LocationExpandedView.id == LinkAgencyLocation.location_id
            )
        )

        if self.location_id is not None:
            query = query.where(
                LocationExpandedView.id == self.location_id
            )
        if self.query is not None:
            query = query.order_by(
                func.similarity(
                    Agency.name,
                    self.query
                ).desc()
            )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query)

        return [
            AgencySearchResponse(
                **mapping
            )
            for mapping in mappings
        ]




