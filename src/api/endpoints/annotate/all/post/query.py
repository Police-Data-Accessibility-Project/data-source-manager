from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.impl.url.suggestion.location.user.sqlalchemy import UserLocationSuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.relevant.user import UserURLTypeSuggestion
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
        relevant_suggestion = UserURLTypeSuggestion(
            url_id=self.url_id,
            user_id=self.user_id,
            type=self.post_info.suggested_status
        )
        session.add(relevant_suggestion)

        # If not relevant, do nothing else
        if not self.post_info.suggested_status in [
            URLType.META_URL,
            URLType.DATA_SOURCE
        ]:
            return

        locations: list[UserLocationSuggestion] = []
        for location_id in self.post_info.location_ids:
            locations.append(UserLocationSuggestion(
                url_id=self.url_id,
                user_id=self.user_id,
                location_id=location_id
            ))
        session.add_all(locations)

        # TODO (TEST): Add test for submitting Meta URL validation
        if self.post_info.record_type is not None:
            record_type_suggestion = UserRecordTypeSuggestion(
                url_id=self.url_id,
                user_id=self.user_id,
                record_type=self.post_info.record_type.value
            )
            session.add(record_type_suggestion)

        for agency_id in self.post_info.agency_ids:
            agency_suggestion = UserUrlAgencySuggestion(
                url_id=self.url_id,
                user_id=self.user_id,
                agency_id=agency_id,
            )
            session.add(agency_suggestion)
