from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.get.models.location import LocationAnnotationResponseOuterInfo
from src.api.endpoints.annotate.all.get.models.suggestion import SuggestionModel
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

        suggestions: list[SuggestionModel] = \
            await requester.get_location_suggestions(self.url_id)
        not_found_count: int = \
            await requester.get_not_found_count(self.url_id)

        return LocationAnnotationResponseOuterInfo(
            suggestions=suggestions,
            not_found_count=not_found_count
        )

