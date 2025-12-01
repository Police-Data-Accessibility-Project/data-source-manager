from typing import Sequence

from sqlalchemy import func, select, RowMapping, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.get.models.agency import AgencyAnnotationSuggestion
from src.db.helpers.query import exists_url
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.user_suggestion_not_found.agency.sqlalchemy import LinkUserSuggestionAgencyNotFound
from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask
from src.db.models.impl.url.suggestion.agency.suggestion.sqlalchemy import AgencyIDSubtaskSuggestion
from src.db.models.impl.url.suggestion.agency.user import UserURLAgencySuggestion
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

    async def get_agency_suggestions(self) -> list[AgencyAnnotationSuggestion]:
        # All agencies with either a user or robo annotation
        valid_agencies_cte = (
            select(
                Agency.id,
            )
            .where(
                or_(
                    exists_url(
                        UserURLAgencySuggestion
                    ),
                    exists_url(
                        URLAutoAgencyIDSubtask
                    )
                )
            )
            .cte("valid_agencies")
        )

        # Number of users who suggested each agency
        user_suggestions_cte = (
            select(
                UserURLAgencySuggestion.url_id,
                UserURLAgencySuggestion.agency_id,
                func.count(UserURLAgencySuggestion.user_id).label('user_count')
            )
            .group_by(
                UserURLAgencySuggestion.agency_id,
                UserURLAgencySuggestion.url_id,
            )
            .cte("user_suggestions")
        )

        # Maximum confidence of robo annotation, if any
        robo_suggestions_cte = (
            select(
                URLAutoAgencyIDSubtask.url_id,
                Agency.id.label("agency_id"),
                func.max(AgencyIDSubtaskSuggestion.confidence).label('robo_confidence')
            )
            .join(
                AgencyIDSubtaskSuggestion,
                AgencyIDSubtaskSuggestion.subtask_id == URLAutoAgencyIDSubtask.id
            )
            .join(
                Agency,
                Agency.id == AgencyIDSubtaskSuggestion.agency_id
            )
            .group_by(
                URLAutoAgencyIDSubtask.url_id,
                Agency.id
            )
            .cte("robo_suggestions")
        )
        # Join user and robo suggestions
        joined_suggestions_query = (
            select(
                valid_agencies_cte.c.id.label("agency_id"),
                Agency.name.label("agency_name"),
                func.coalesce(user_suggestions_cte.c.user_count, 0).label('user_count'),
                func.coalesce(robo_suggestions_cte.c.robo_confidence, 0).label('robo_confidence'),
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
                robo_suggestions_cte,
                and_(
                    robo_suggestions_cte.c.url_id == self.url_id,
                    robo_suggestions_cte.c.agency_id == Agency.id
                )
            )
            .where(
                or_(
                    user_suggestions_cte.c.user_count > 0,
                    robo_suggestions_cte.c.robo_confidence > 0
                )
            )
        )

        # Return suggestions
        mappings: Sequence[RowMapping] = await self.mappings(joined_suggestions_query)
        suggestions: list[AgencyAnnotationSuggestion] = [
            AgencyAnnotationSuggestion(
                **mapping
            )
            for mapping in mappings
        ]
        return suggestions

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