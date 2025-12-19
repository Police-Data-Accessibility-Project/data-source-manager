from typing import Sequence

from sqlalchemy import select, func, RowMapping, or_, and_

from src.api.endpoints.annotate.all.get.models.suggestion import SuggestionModel
from src.api.endpoints.annotate.all.get.queries._shared.sort import sort_suggestions
from src.db.helpers.query import exists_url
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.annotation.location.auto.subtask.sqlalchemy import AnnotationLocationAutoSubtask
from src.db.models.impl.annotation.location.auto.suggestion.sqlalchemy import AnnotationLocationAutoSuggestion
from src.db.models.impl.annotation.location.user.sqlalchemy import AnnotationLocationUser
from src.db.models.impl.link.user_suggestion_not_found.location.sqlalchemy import LinkUserSuggestionLocationNotFound
from src.db.models.views.location_expanded import LocationExpandedView
from src.db.templates.requester import RequesterBase


class GetLocationSuggestionsRequester(RequesterBase):

    async def get_location_suggestions(self, url_id: int) -> list[SuggestionModel]:
        # All locations with either a user or robo annotation
        valid_locations_cte = (
            select(
                LocationExpandedView.id,
            )
            .where(
                or_(
                    exists_url(
                        AnnotationLocationUser
                    ),
                    exists_url(
                        AnnotationLocationAutoSubtask
                    )
                )
            )
            .cte("valid_locations")
        )
        # Number of users who suggested each location
        user_suggestions_cte = (
            select(
                AnnotationLocationUser.url_id,
                AnnotationLocationUser.location_id,
                func.count(AnnotationLocationUser.user_id).label('user_count')
            )
            .group_by(
                AnnotationLocationUser.location_id,
                AnnotationLocationUser.url_id,
            )
            .cte("user_suggestions")
        )
        # Maximum confidence of robo annotation, if any
        robo_suggestions_cte = (
            select(
                AnnotationLocationAutoSubtask.url_id,
                LocationExpandedView.id.label("location_id"),
                func.max(AnnotationLocationAutoSuggestion.confidence).label('robo_confidence')
            )
            .join(
                LocationExpandedView,
                LocationExpandedView.id == AnnotationLocationAutoSuggestion.location_id
            )
            .join(
                AnnotationLocationAutoSubtask,
                AnnotationLocationAutoSubtask.id == AnnotationLocationAutoSuggestion.subtask_id
            )
            .group_by(
                LocationExpandedView.id,
                AnnotationLocationAutoSubtask.url_id,
            )
            .cte("robo_suggestions")
        )
        # Join user and robo suggestions
        joined_suggestions_query = (
            select(
                valid_locations_cte.c.id,
                LocationExpandedView.full_display_name.label("display_name"),
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
        suggestions: list[SuggestionModel] = [
            SuggestionModel(
                **mapping
            )
            for mapping in mappings
        ]
        return sort_suggestions(suggestions)

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