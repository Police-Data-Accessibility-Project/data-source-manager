from collections import defaultdict
from typing import Any, Sequence

from sqlalchemy import values, column, String, Integer, func, select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.query_.models.params import \
    SearchSimilarLocationsParams
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.query_.models.response import \
    SearchSimilarLocationsOuterResponse, SearchSimilarLocationsLocationInfo, SearchSimilarLocationsResponse
from src.db.models.views.location_expanded import LocationExpandedView
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class SearchSimilarLocationsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        params: list[SearchSimilarLocationsParams]
    ):
        super().__init__()
        self.params = params

    async def run(self, session: AsyncSession) -> SearchSimilarLocationsOuterResponse:
        queries_as_tups: list[tuple[int, str, str]] = [
            (
                param.request_id,
                param.query,
                param.iso,
            )
            for param in self.params
        ]

        vals = (
            values(
                column("request_id", Integer),
                column("query", String),
                column("iso", String),
                name="input_queries",
            )
            .data(queries_as_tups)
            .alias("input_queries_alias")
        )

        similarity = func.similarity(
            vals.c.query,
            LocationExpandedView.display_name,
        )

        lateral_top_5 = (
            select(
                vals.c.request_id,
                LocationExpandedView.location_id,
                similarity.label("similarity"),
            )
            .join(
                LocationExpandedView,
                LocationExpandedView.state_iso == vals.c.iso,
            )
            .order_by(
                similarity.desc(),
            )
            .limit(5)
            .lateral("lateral_top_5")
        )

        final = select(
            vals.c.request_id,
            lateral_top_5.c.location_id,
            lateral_top_5.c.similarity,
        ).join(
            lateral_top_5,
            vals.c.request_id == lateral_top_5.c.request_id,
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=final)
        request_id_to_locations: dict[int, list[SearchSimilarLocationsLocationInfo]] = (
            defaultdict(list)
        )
        for mapping in mappings:
            inner_response = SearchSimilarLocationsLocationInfo(
                location_id=mapping["location_id"],
                similarity=mapping["similarity"],
            )
            request_id: int = mapping["request_id"]
            request_id_to_locations[request_id].append(inner_response)

        responses: list[SearchSimilarLocationsResponse] = []
        for request_id, inner_responses in request_id_to_locations.items():
            sorted_responses: list[SearchSimilarLocationsLocationInfo] = sorted(
                inner_responses,
                key=lambda x: x.similarity,
                reverse=True,
            )
            request_level_response = SearchSimilarLocationsResponse(
                request_id=request_id,
                results=sorted_responses,
            )
            responses.append(request_level_response)

        return SearchSimilarLocationsOuterResponse(
            responses=responses,
        )

