from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.get.models.location import LocationAnnotationResponseOuterInfo, \
    LocationAnnotationUserSuggestion, LocationAnnotationAutoSuggestion, LocationAnnotationUserSuggestionOuterInfo
from src.api.endpoints.annotate.all.get.queries.location_.requester import GetLocationSuggestionsRequester
from src.db.queries.base.builder import QueryBuilderBase
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.get.models.location import LocationAnnotationResponseOuterInfo, \
    LocationAnnotationUserSuggestion, LocationAnnotationAutoSuggestion
from src.api.endpoints.annotate.all.get.queries.location_.requester import GetLocationSuggestionsRequester
from src.db.queries.base.builder import QueryBuilderBase


class GetLocationSuggestionsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int
    ):
        super().__init__()
        self.url_id = url_id


    async def run(self, session: AsyncSession) -> LocationAnnotationResponseOuterInfo:
        requester = GetLocationSuggestionsRequester(session)

        # TODO: Pull both in single query
        suggestions
        user_suggestions: list[LocationAnnotationUserSuggestion] = \
            await requester.get_user_location_suggestions(self.url_id)
        auto_suggestions: list[LocationAnnotationAutoSuggestion] = \
            await requester.get_auto_location_suggestions(self.url_id)
        not_found_count: int = \
            await requester.get_not_found_count(self.url_id)

        return LocationAnnotationResponseOuterInfo(
            user=LocationAnnotationUserSuggestionOuterInfo(
                suggestions=user_suggestions,
                not_found_count=not_found_count
            ),
            auto=auto_suggestions
        )

