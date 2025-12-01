from typing import Sequence

from sqlalchemy import select, func, RowMapping, or_, and_

from src.api.endpoints.annotate.all.get.models.location import LocationAnnotationSuggestion
from src.db.helpers.query import exists_url
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.link.user_suggestion_not_found.location.sqlalchemy import LinkUserSuggestionLocationNotFound
from src.db.models.impl.url.suggestion.location.auto.subtask.sqlalchemy import AutoLocationIDSubtask
from src.db.models.impl.url.suggestion.location.auto.suggestion.sqlalchemy import LocationIDSubtaskSuggestion
from src.db.models.impl.url.suggestion.location.user.sqlalchemy import UserLocationSuggestion
from src.db.models.views.location_expanded import LocationExpandedView
from src.db.templates.requester import RequesterBase


class GetLocationSuggestionsRequester(RequesterBase):

    async def get_location_suggestions(self, url_id: int) -> list[LocationAnnotationSuggestion]:
        # All locations with either a user or robo annotation
        valid_locations_cte = (
            select(
                LocationExpandedView.id,
            )
            .where(
                or_(
                    exists_url(
                        UserLocationSuggestion
                    ),
                    exists_url(
                        AutoLocationIDSubtask
                    )
                )
            )
            .cte("valid_locations")
        )
        # Number of users who suggested each location
        user_suggestions_cte = (
            select(
                UserLocationSuggestion.url_id,
                UserLocationSuggestion.location_id,
                func.count(UserLocationSuggestion.user_id).label('user_count')
            )
            .group_by(
                UserLocationSuggestion.location_id,
                UserLocationSuggestion.url_id,
            )
            .cte("user_suggestions")
        )
        # Maximum confidence of robo annotation, if any
        robo_suggestions_cte = (
            select(
                AutoLocationIDSubtask.url_id,
                LocationExpandedView.id.label("location_id"),
                func.max(LocationIDSubtaskSuggestion.confidence).label('robo_confidence')
            )
            .join(
                LocationExpandedView,
                LocationExpandedView.id == LocationIDSubtaskSuggestion.location_id
            )
            .join(
                AutoLocationIDSubtask,
                AutoLocationIDSubtask.id == LocationIDSubtaskSuggestion.subtask_id
            )
            .group_by(
                LocationExpandedView.id,
                AutoLocationIDSubtask.url_id,
            )
            .cte("robo_suggestions")
        )
        # Join user and robo suggestions
        joined_suggestions_query = (
            select(
                valid_locations_cte.c.id.label("location_id"),
                LocationExpandedView.full_display_name.label("location_name"),
                func.coalesce(user_suggestions_cte.c.user_count, 0).label("user_count"),
                func.coalesce(robo_suggestions_cte.c.robo_confidence, 0).label("robo_confidence"),
            )
            .join(
                LocationExpandedView,
                LocationExpandedView.id == valid_locations_cte.c.id
            )
            .outerjoin(
                user_suggestions_cte,
                and_(
                    user_suggestions_cte.c.url_id == url_id,
                    user_suggestions_cte.c.location_id == LocationExpandedView.id
                )
            )
            .outerjoin(
                robo_suggestions_cte,
                and_(
                    robo_suggestions_cte.c.url_id == url_id,
                    robo_suggestions_cte.c.location_id == LocationExpandedView.id
                )
            )
            .where(
                or_(
                    user_suggestions_cte.c.user_count > 0,
                    robo_suggestions_cte.c.robo_confidence > 0
                )
            )
        )

        mappings: Sequence[RowMapping] = await self.mappings(joined_suggestions_query)
        suggestions: list[LocationAnnotationSuggestion] = [
            LocationAnnotationSuggestion(
                **mapping
            )
            for mapping in mappings
        ]
        return suggestions


    async def get_not_found_count(self, url_id: int) -> int:
        query = (
            select(
                func.count(LinkUserSuggestionLocationNotFound.user_id)
            )
            .where(
                LinkUserSuggestionLocationNotFound.url_id == url_id
            )
        )

        return await sh.scalar(self.session, query=query)