from sqlalchemy import CTE, select, func, Column

from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask
from src.db.models.impl.url.suggestion.agency.suggestion.sqlalchemy import AgencyIDSubtaskSuggestion

SUGGESTIONS_WITH_HIGHEST_CONFIDENCE_CTE: CTE = (
    select(
        URLAutoAgencyIDSubtask.url_id,
        AgencyIDSubtaskSuggestion.agency_id,
        func.max(AgencyIDSubtaskSuggestion.confidence)
    )
    .select_from(URLAutoAgencyIDSubtask)
    .join(
        AgencyIDSubtaskSuggestion,
        URLAutoAgencyIDSubtask.id == AgencyIDSubtaskSuggestion.subtask_id
    )
    .group_by(
        URLAutoAgencyIDSubtask.url_id,
        AgencyIDSubtaskSuggestion.agency_id
    )
    .cte("suggestions_with_highest_confidence")
)

class SuggestionsWithHighestConfidenceCTE:

    def __init__(self):
        self._cte = (
            select(
                URLAutoAgencyIDSubtask.url_id,
                AgencyIDSubtaskSuggestion.agency_id,
                func.max(AgencyIDSubtaskSuggestion.confidence).label("confidence")
            )
            .select_from(URLAutoAgencyIDSubtask)
            .join(
                AgencyIDSubtaskSuggestion,
                URLAutoAgencyIDSubtask.id == AgencyIDSubtaskSuggestion.subtask_id
            )
            .where(
                AgencyIDSubtaskSuggestion.agency_id.isnot(None)
            )
            .group_by(
                URLAutoAgencyIDSubtask.url_id,
                AgencyIDSubtaskSuggestion.agency_id
            )
            .cte("suggestions_with_highest_confidence")
        )

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def url_id(self) -> Column[int]:
        return self._cte.columns.url_id

    @property
    def agency_id(self) -> Column[int]:
        return self._cte.columns.agency_id

    @property
    def confidence(self) -> Column[float]:
        return self._cte.columns.confidence