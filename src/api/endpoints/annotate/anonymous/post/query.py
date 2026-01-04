from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.db.models.impl.annotation.agency.anon.sqlalchemy import AnnotationAgencyAnon
from src.db.models.impl.annotation.location.anon.sqlalchemy import AnnotationLocationAnon
from src.db.models.impl.annotation.name.suggestion.enums import NameSuggestionSource
from src.db.models.impl.annotation.name.suggestion.sqlalchemy import AnnotationNameSuggestion
from src.db.models.impl.annotation.record_type.anon.sqlalchemy import AnnotationRecordTypeAnon
from src.db.models.impl.annotation.url_type.anon.sqlalchemy import AnnotationURLTypeAnon
from src.db.models.impl.annotation.name.anon.sqlalchemy import AnnotationNameAnonEndorsement
from src.db.queries.base.builder import QueryBuilderBase


class AddAnonymousAnnotationsToURLQueryBuilder(QueryBuilderBase):
    def __init__(
        self,
        session_id: UUID,
        url_id: int,
        post_info: AllAnnotationPostInfo
    ):
        super().__init__()
        self.session_id = session_id
        self.url_id = url_id
        self.post_info = post_info

    async def run(self, session: AsyncSession) -> None:

        url_type_suggestion = AnnotationURLTypeAnon(
            url_id=self.url_id,
            url_type=self.post_info.suggested_status,
            session_id=self.session_id
        )
        session.add(url_type_suggestion)

        name_id: int | None
        if self.post_info.name_info.new_name is not None:
            name_suggestion = AnnotationNameSuggestion(
                url_id=self.url_id,
                suggestion=self.post_info.name_info.new_name,
                source=NameSuggestionSource.USER
            )
            session.add(name_suggestion)
            await session.flush()
            name_id = name_suggestion.id
        elif self.post_info.name_info.existing_name_id is not None:
            name_id = self.post_info.name_info.existing_name_id
        else:
            name_id = None

        if name_id is not None:
            name_suggestion = AnnotationNameAnonEndorsement(
                suggestion_id=name_id,
                session_id=self.session_id
            )
            session.add(name_suggestion)

        if self.post_info.record_type is not None:
            record_type_suggestion = AnnotationRecordTypeAnon(
                url_id=self.url_id,
                record_type=self.post_info.record_type,
                session_id=self.session_id
            )
            session.add(record_type_suggestion)

        if len(self.post_info.location_info.location_ids) != 0:
            location_suggestions = [
                AnnotationLocationAnon(
                    url_id=self.url_id,
                    location_id=location_id,
                    session_id=self.session_id
                )
                for location_id in self.post_info.location_info.location_ids
            ]
            session.add_all(location_suggestions)

        if len(self.post_info.agency_info.agency_ids) != 0:
            agency_suggestions = [
                AnnotationAgencyAnon(
                    url_id=self.url_id,
                    agency_id=agency_id,
                    session_id=self.session_id
                )
                for agency_id in self.post_info.agency_info.agency_ids
            ]
            session.add_all(agency_suggestions)

