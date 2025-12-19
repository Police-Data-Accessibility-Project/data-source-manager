from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.post.models.name import AnnotationPostNameInfo
from src.core.enums import RecordType
from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.location.user.sqlalchemy import AnnotationLocationUser
from src.db.models.impl.annotation.name.suggestion.enums import NameSuggestionSource
from src.db.models.impl.annotation.name.suggestion.sqlalchemy import AnnotationNameSuggestion
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.annotation.name.user.sqlalchemy import LinkUserNameSuggestion
from src.db.models.impl.link.user_suggestion_not_found.agency.sqlalchemy import LinkUserSuggestionAgencyNotFound
from src.db.models.impl.link.user_suggestion_not_found.location.sqlalchemy import LinkUserSuggestionLocationNotFound
from src.db.models.impl.annotation.record_type.user.user import AnnotationUserRecordType
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationUserURLType
from src.db.templates.requester import RequesterBase


class AddAllAnnotationsToURLRequester(RequesterBase):

    def __init__(
        self,
        session: AsyncSession,
        url_id: int,
        user_id: int,
    ):
        super().__init__(session=session)
        self.url_id = url_id
        self.user_id = user_id

    def optionally_add_record_type(
        self,
        rt: RecordType | None,
    ) -> None:
        if rt is None:
            return
        record_type_suggestion = AnnotationUserRecordType(
            url_id=self.url_id,
            user_id=self.user_id,
            record_type=rt.value
        )
        self.session.add(record_type_suggestion)

    def add_relevant_annotation(
        self,
        url_type: URLType,
    ) -> None:
        relevant_suggestion = AnnotationUserURLType(
            url_id=self.url_id,
            user_id=self.user_id,
            type=url_type
        )
        self.session.add(relevant_suggestion)

    def add_agency_ids(self, agency_ids: list[int]) -> None:
        for agency_id in agency_ids:
            agency_suggestion = AnnotationAgencyUser(
                url_id=self.url_id,
                user_id=self.user_id,
                agency_id=agency_id,
            )
            self.session.add(agency_suggestion)

    def add_location_ids(self, location_ids: list[int]) -> None:
        locations: list[AnnotationLocationUser] = []
        for location_id in location_ids:
            locations.append(AnnotationLocationUser(
                url_id=self.url_id,
                user_id=self.user_id,
                location_id=location_id
            ))
        self.session.add_all(locations)

    async def optionally_add_name_suggestion(
        self,
        name_info: AnnotationPostNameInfo
    ) -> None:
        if name_info.empty:
            return
        if name_info.existing_name_id is not None:
            link = LinkUserNameSuggestion(
                user_id=self.user_id,
                suggestion_id=name_info.existing_name_id,
            )
            self.session.add(link)
            return
        name_suggestion = AnnotationNameSuggestion(
            url_id=self.url_id,
            suggestion=name_info.new_name,
            source=NameSuggestionSource.USER
        )
        self.session.add(name_suggestion)
        await self.session.flush()
        link = LinkUserNameSuggestion(
            user_id=self.user_id,
            suggestion_id=name_suggestion.id,
        )
        self.session.add(link)

    def add_not_found_agency(self) -> None:
        not_found_agency = LinkUserSuggestionAgencyNotFound(
            user_id=self.user_id,
            url_id=self.url_id,
        )
        self.session.add(not_found_agency)

    def add_not_found_location(self) -> None:
        not_found_location = LinkUserSuggestionLocationNotFound(
            user_id=self.user_id,
            url_id=self.url_id,
        )
        self.session.add(not_found_location)
