from typing import Sequence

from sqlalchemy import select, func, RowMapping

from src.api.endpoints.annotate.all.get.models.location import LocationAnnotationUserSuggestion, \
    LocationAnnotationAutoSuggestion
from src.db.models.impl.link.user_suggestion_not_found.location.sqlalchemy import LinkUserSuggestionLocationNotFound
from src.db.models.impl.url.suggestion.location.auto.subtask.sqlalchemy import AutoLocationIDSubtask
from src.db.models.impl.url.suggestion.location.auto.suggestion.sqlalchemy import LocationIDSubtaskSuggestion
from src.db.models.impl.url.suggestion.location.user.sqlalchemy import UserLocationSuggestion
from src.db.models.views.location_expanded import LocationExpandedView
from src.db.templates.requester import RequesterBase

from src.db.helpers.session import session_helper as sh

class GetLocationSuggestionsRequester(RequesterBase):


    async def get_user_location_suggestions(self, url_id: int) -> list[LocationAnnotationUserSuggestion]:
        query = (
            select(
                UserLocationSuggestion.location_id,
                LocationExpandedView.display_name.label("location_name"),
                func.count(UserLocationSuggestion.user_id).label('user_count')
            )
            .join(
                LocationExpandedView,
                LocationExpandedView.id == UserLocationSuggestion.location_id
            )
            .where(
                UserLocationSuggestion.url_id == url_id
            )
            .group_by(
                UserLocationSuggestion.location_id,
                LocationExpandedView.display_name
            )
            .order_by(
                func.count(UserLocationSuggestion.user_id).desc()
            )
        )
        raw_results: Sequence[RowMapping] = await sh.mappings(self.session, query)
        return [
            LocationAnnotationUserSuggestion(
                **raw_result
            )
            for raw_result in raw_results
        ]



    async def get_auto_location_suggestions(
        self,
        url_id: int
    ) -> list[LocationAnnotationAutoSuggestion]:
        query = (
            select(
                LocationExpandedView.display_name.label("location_name"),
                LocationIDSubtaskSuggestion.location_id,
                LocationIDSubtaskSuggestion.confidence,
            )
            .join(
                LocationExpandedView,
                LocationExpandedView.id == LocationIDSubtaskSuggestion.location_id
            )
            .join(
                AutoLocationIDSubtask,
                AutoLocationIDSubtask.id == LocationIDSubtaskSuggestion.subtask_id
            )
            .where(
                AutoLocationIDSubtask.url_id == url_id
            )
            .order_by(
                LocationIDSubtaskSuggestion.confidence.desc()
            )
        )
        raw_results: Sequence[RowMapping] = await sh.mappings(self.session, query)
        return [
            LocationAnnotationAutoSuggestion(
                **raw_result
            )
            for raw_result in raw_results
        ]

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