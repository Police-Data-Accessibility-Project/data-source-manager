from typing import Sequence

from sqlalchemy import func, select, RowMapping, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.get.models.suggestion import SuggestionModel
from src.api.endpoints.annotate.all.get.queries._shared.sort import sort_suggestions
from src.db.helpers.query import exists_url
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.annotation.agency.anon.sqlalchemy import AnnotationAgencyAnon
from src.db.models.impl.annotation.agency.auto.subtask.sqlalchemy import AnnotationAgencyAutoSubtask
from src.db.models.impl.annotation.agency.auto.suggestion.sqlalchemy import AnnotationAgencyAutoSuggestion
from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.link.user_suggestion_not_found.agency.sqlalchemy import LinkUserSuggestionAgencyNotFound
from src.db.templates.requester import RequesterBase


class GetAgencySuggestionsRequester(RequesterBase):

    def __init__(
        self,
        session: AsyncSession,
        url_id: int,
        location_id: int
    ):
        super().__init__(session)
        self.url_id = url_id
        self.location_id = location_id

    async def get_agency_suggestions(self) -> list[SuggestionModel]:
        # All agencies with either a user or robo annotation
        valid_agencies_cte = (
            select(
                Agency.id,
            )
            .where(
                or_(
                    exists_url(
                        AnnotationAgencyUser
                    ),
                    exists_url(
                        AnnotationAgencyAutoSubtask
                    ),
                    exists_url(
                        AnnotationAgencyAnon
                    )
                )
            )
            .cte("valid_agencies")
        )

        # Number of users who suggested each agency
        user_suggestions_cte = (
            select(
                AnnotationAgencyUser.url_id,
                AnnotationAgencyUser.agency_id,
                func.count(AnnotationAgencyUser.user_id).label('user_count')
            )
            .group_by(
                AnnotationAgencyUser.agency_id,
                AnnotationAgencyUser.url_id,
            )
            .cte("user_suggestions")
        )

        # Number of anon users who suggested each agency
        anon_suggestions_cte = (
            select(
                AnnotationAgencyAnon.url_id,
                AnnotationAgencyAnon.agency_id,
                func.count(AnnotationAgencyAnon.session_id).label('anon_count')
            )
            .group_by(
                AnnotationAgencyAnon.agency_id,
                AnnotationAgencyAnon.url_id,
            )
            .cte("anon_suggestions")
        )

        # Maximum confidence of robo annotation, if any
        robo_suggestions_cte = (
            select(
                AnnotationAgencyAutoSubtask.url_id,
                Agency.id.label("agency_id"),
                func.max(AnnotationAgencyAutoSuggestion.confidence).label('robo_confidence')
            )
            .join(
                AnnotationAgencyAutoSuggestion,
                AnnotationAgencyAutoSuggestion.subtask_id == AnnotationAgencyAutoSubtask.id
            )
            .join(
                Agency,
                Agency.id == AnnotationAgencyAutoSuggestion.agency_id
            )
            .group_by(
                AnnotationAgencyAutoSubtask.url_id,
                Agency.id
            )
            .cte("robo_suggestions")
        )
        # Join user and robo suggestions
        joined_suggestions_query = (
            select(
                valid_agencies_cte.c.id,
                Agency.name.label("display_name"),
                func.coalesce(user_suggestions_cte.c.user_count, 0).label('user_count'),
                func.coalesce(robo_suggestions_cte.c.robo_confidence, 0).label('robo_confidence'),
                func.coalesce(anon_suggestions_cte.c.anon_count, 0).label('anon_count'),
            )
            .join(
                Agency,
                Agency.id == valid_agencies_cte.c.id
            )
            .outerjoin(
                user_suggestions_cte,
                and_(
                    user_suggestions_cte.c.url_id == self.url_id,
                    user_suggestions_cte.c.agency_id == Agency.id
                )
            )
            .outerjoin(
                anon_suggestions_cte,
                and_(
                    anon_suggestions_cte.c.url_id == self.url_id,
                    anon_suggestions_cte.c.agency_id == Agency.id
                )
            )
            .outerjoin(
                robo_suggestions_cte,
                and_(
                    robo_suggestions_cte.c.url_id == self.url_id,
                    robo_suggestions_cte.c.agency_id == Agency.id
                )
            )
            .where(
                or_(
                    user_suggestions_cte.c.user_count > 0,
                    robo_suggestions_cte.c.robo_confidence > 0,
                    anon_suggestions_cte.c.anon_count > 0
                )
            )
        )

        # Return suggestions
        mappings: Sequence[RowMapping] = await self.mappings(joined_suggestions_query)
        suggestions: list[SuggestionModel] = [
            SuggestionModel(
                id=mapping["id"],
                display_name=mapping["display_name"],
                user_count=mapping['user_count'] + (mapping['anon_count'] // 2),
                robo_confidence=mapping["robo_confidence"]
            )
            for mapping in mappings
        ]
        return sort_suggestions(suggestions)

    async def get_not_found_count(self) -> int:
        query = (
            select(
                func.count(LinkUserSuggestionAgencyNotFound.user_id)
            )
            .where(
                LinkUserSuggestionAgencyNotFound.url_id == self.url_id
            )
        )

        return await sh.scalar(self.session, query=query)