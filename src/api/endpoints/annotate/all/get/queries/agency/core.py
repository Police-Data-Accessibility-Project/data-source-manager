from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.get.models.agency import AgencyAnnotationResponseOuterInfo
from src.api.endpoints.annotate.all.get.models.agency import AgencyAnnotationSuggestion
from src.api.endpoints.annotate.all.get.queries.agency.requester import GetAgencySuggestionsRequester
from src.db.queries.base.builder import QueryBuilderBase


class GetAgencySuggestionsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int,
        location_id: int | None = None
    ):
        super().__init__()
        self.url_id = url_id
        self.location_id = location_id

    async def run(self, session: AsyncSession) -> AgencyAnnotationResponseOuterInfo:
        requester = GetAgencySuggestionsRequester(
            session,
            url_id=self.url_id,
            location_id=self.location_id
        )

        suggestions: list[AgencyAnnotationSuggestion] = \
            await requester.get_agency_suggestions()
        not_found_count: int = \
            await requester.get_not_found_count()
        return AgencyAnnotationResponseOuterInfo(
            suggestions=suggestions,
            not_found_count=not_found_count
        )


