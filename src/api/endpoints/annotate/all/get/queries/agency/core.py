from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.get.models.agency import AgencyAnnotationResponseOuterInfo, \
    AgencyAnnotationUserSuggestionOuterInfo, AgencyAnnotationUserSuggestion, AgencyAnnotationAutoSuggestion
from src.api.endpoints.annotate.all.get.queries.agency.requester import GetAgencySuggestionsRequester
from src.db.queries.base.builder import QueryBuilderBase
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.get.models.agency import AgencyAnnotationResponseOuterInfo, \
    AgencyAnnotationUserSuggestionOuterInfo, AgencyAnnotationUserSuggestion, AgencyAnnotationAutoSuggestion
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

        # TODO: Pull both in single query
        user_suggestions: list[AgencyAnnotationUserSuggestion] = \
            await requester.get_user_agency_suggestions()
        auto_suggestions: list[AgencyAnnotationAutoSuggestion] = \
            await requester.get_auto_agency_suggestions()
        not_found_count: int = \
            await requester.get_not_found_count()
        return AgencyAnnotationResponseOuterInfo(
            user=AgencyAnnotationUserSuggestionOuterInfo(
                suggestions=user_suggestions,
                not_found_count=not_found_count
            ),
            auto=auto_suggestions,
        )


