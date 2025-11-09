from typing import Sequence

from sqlalchemy import select, func, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.search.agency.ctes.with_location_id import WithLocationIdCTEContainer
from src.api.endpoints.search.agency.models.response import AgencySearchResponse
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.agency.enums import JurisdictionType
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.models.views.location_expanded import LocationExpandedView
from src.db.queries.base.builder import QueryBuilderBase


class SearchAgencyQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        location_id: int | None,
        query: str | None,
        jurisdiction_type: JurisdictionType | None,
    ):
        super().__init__()
        self.location_id = location_id
        self.query = query
        self.jurisdiction_type = jurisdiction_type

    async def run(self, session: AsyncSession) -> list[AgencySearchResponse]:

        query = (
            select(
                Agency.id.label("agency_id"),
                Agency.name.label("agency_name"),
                Agency.jurisdiction_type,
                Agency.agency_type,
                LocationExpandedView.display_name.label("location_display_name")
            )
        )
        if self.location_id is None:
            query = query.join(
                LinkAgencyLocation,
                LinkAgencyLocation.agency_id == Agency.id
            ).join(
                LocationExpandedView,
                LocationExpandedView.id == LinkAgencyLocation.location_id
            )
        else:
            with_location_id_cte_container = WithLocationIdCTEContainer(self.location_id)
            query = query.join(
                with_location_id_cte_container.cte,
                with_location_id_cte_container.agency_id == Agency.id
            ).join(
                LocationExpandedView,
                LocationExpandedView.id == with_location_id_cte_container.location_id
            )

        if self.jurisdiction_type is not None:
            query = query.where(
                Agency.jurisdiction_type == self.jurisdiction_type
            )

        if self.query is not None:
            query = query.order_by(
                func.similarity(
                    Agency.name,
                    self.query
                ).desc()
            )

        query = query.limit(50)

        mappings: Sequence[RowMapping] = await sh.mappings(session, query)

        return [
            AgencySearchResponse(
                **mapping
            )
            for mapping in mappings
        ]




