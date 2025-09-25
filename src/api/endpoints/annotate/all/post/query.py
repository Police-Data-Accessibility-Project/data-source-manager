from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.api.endpoints.annotate.all.post.requester import AddAllAnnotationsToURLRequester
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
        requester = AddAllAnnotationsToURLRequester(
            session=session,
            url_id=self.url_id,
            user_id=self.user_id
        )

        # Add relevant annotation
        requester.add_relevant_annotation(self.post_info.suggested_status)

        await requester.optionally_add_name_suggestion(self.post_info.name_info)


        # If not relevant, do nothing else
        if self.post_info.suggested_status == URLType.NOT_RELEVANT:
            return

        requester.add_location_ids(self.post_info.location_ids)

        # TODO (TEST): Add test for submitting Meta URL validation
        requester.optionally_add_record_type(self.post_info.record_type)

        requester.add_agency_ids(self.post_info.agency_ids)
