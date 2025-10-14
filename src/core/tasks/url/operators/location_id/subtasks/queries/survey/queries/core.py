from collections import Counter

from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.location_id.subtasks.queries.survey.constants import SUBTASK_HIERARCHY_MAPPING
from src.core.tasks.url.operators.location_id.subtasks.queries.survey.queries.eligible_counts import \
    ELIGIBLE_COUNTS_QUERY
from src.db.models.impl.url.suggestion.location.auto.subtask.enums import LocationIDSubtaskType
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class LocationIDSurveyQueryBuilder(QueryBuilderBase):
    """
    Survey applicable URLs to determine next subtask to run

    URLs are "inapplicable" if they have any of the following properties:
    - Are validated via FlagURLValidated model
    - Have at least one annotation with agency suggestion with confidence >= 95
    - Have all possible subtasks completed

    Returns a list of one or more subtasks to run
    based on which subtask(s) have the most applicable URLs
    (or an empty list if no subtasks have applicable URLs)
    """

    def __init__(
        self,
        allowed_subtasks: list[LocationIDSubtaskType]
    ):
        super().__init__()
        self._allowed_subtasks = allowed_subtasks

    async def run(self, session: AsyncSession) -> LocationIDSubtaskType | None:
        results: RowMapping = await sh.mapping(session, ELIGIBLE_COUNTS_QUERY)
        counts: Counter[str] = Counter(results)

        allowed_counts: Counter[str] = await self._filter_allowed_counts(counts)
        if len(allowed_counts) == 0:
            return None
        max_count: int = max(allowed_counts.values())
        if max_count == 0:
            return None
        subtasks_with_max_count: list[str] = [
            subtask for subtask, count in allowed_counts.items()
            if count == max_count
        ]
        subtasks_as_enum_list: list[LocationIDSubtaskType] = [
            LocationIDSubtaskType(subtask)
            for subtask in subtasks_with_max_count
        ]
        # Sort subtasks by priority
        sorted_subtasks: list[LocationIDSubtaskType] = sorted(
            subtasks_as_enum_list,
            key=lambda subtask: SUBTASK_HIERARCHY_MAPPING[subtask],
            reverse=True,
        )
        # Return the highest priority subtask
        return sorted_subtasks[0]

    async def _filter_allowed_counts(self, counts: Counter[str]) -> Counter[str]:
        return Counter(
            {
                subtask: count
                for subtask, count in counts.items()
                if LocationIDSubtaskType(subtask) in self._allowed_subtasks
            }
        )




