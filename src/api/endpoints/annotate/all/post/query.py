from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.core.enums import SuggestedStatus
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.impl.url.suggestion.location.user.sqlalchemy import UserLocationSuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.relevant.user import UserRelevantSuggestion
from src.db.queries.base.builder import QueryBuilderBase


class AddAllAnnotationsToURLQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        user_id: int,
        url_id: int,
        post_info: AllAnnotationPostInfo
    ):
        super().__init__()
        self.user_id = user_id
        self.url_id = url_id
        self.post_info = post_info


    async def run(self, session: AsyncSession) -> None:
        # Add relevant annotation
        relevant_suggestion = UserRelevantSuggestion(
            url_id=self.url_id,
            user_id=self.user_id,
            suggested_status=self.post_info.suggested_status.value
        )
        session.add(relevant_suggestion)

        # If not relevant, do nothing else
        # TODO: 1: Update to account for change in SuggestedStatus
        if not self.post_info.suggested_status == SuggestedStatus.RELEVANT:
            return

        locations: list[UserLocationSuggestion] = []
        for location_id in self.post_info.location_ids:
            locations.append(UserLocationSuggestion(
                url_id=self.url_id,
                user_id=self.user_id,
                location_id=location_id
            ))
        session.add_all(locations)

        record_type_suggestion = UserRecordTypeSuggestion(
            url_id=self.url_id,
            user_id=self.user_id,
            record_type=self.post_info.record_type.value
        )
        session.add(record_type_suggestion)

        agency_suggestion = UserUrlAgencySuggestion(
            url_id=self.url_id,
            user_id=self.user_id,
            agency_id=self.post_info.agency.suggested_agency,
            is_new=self.post_info.agency.is_new
        )
        session.add(agency_suggestion)
