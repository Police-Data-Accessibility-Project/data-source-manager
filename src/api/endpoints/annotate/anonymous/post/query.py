from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.db.models.impl.url.suggestion.anonymous.agency.sqlalchemy import AnonymousAnnotationAgency
from src.db.models.impl.url.suggestion.anonymous.location.sqlalchemy import AnonymousAnnotationLocation
from src.db.models.impl.url.suggestion.anonymous.record_type.sqlalchemy import AnonymousAnnotationRecordType
from src.db.models.impl.url.suggestion.anonymous.url_type.sqlalchemy import AnonymousAnnotationURLType
from src.db.queries.base.builder import QueryBuilderBase


class AddAnonymousAnnotationsToURLQueryBuilder(QueryBuilderBase):
    def __init__(
        self,
        url_id: int,
        post_info: AllAnnotationPostInfo
    ):
        super().__init__()
        self.url_id = url_id
        self.post_info = post_info

    async def run(self, session: AsyncSession) -> None:

        url_type_suggestion = AnonymousAnnotationURLType(
            url_id=self.url_id,
            url_type=self.post_info.suggested_status
        )
        session.add(url_type_suggestion)

        if self.post_info.record_type is not None:
            record_type_suggestion = AnonymousAnnotationRecordType(
                url_id=self.url_id,
                record_type=self.post_info.record_type
            )
            session.add(record_type_suggestion)

        if len(self.post_info.location_info.location_ids) != 0:
            location_suggestions = [
                AnonymousAnnotationLocation(
                    url_id=self.url_id,
                    location_id=location_id
                )
                for location_id in self.post_info.location_info.location_ids
            ]
            session.add_all(location_suggestions)

        if len(self.post_info.agency_info.agency_ids) != 0:
            agency_suggestions = [
                AnonymousAnnotationAgency(
                    url_id=self.url_id,
                    agency_id=agency_id
                )
                for agency_id in self.post_info.agency_info.agency_ids
            ]
            session.add_all(agency_suggestions)

        # Ignore Name suggestions