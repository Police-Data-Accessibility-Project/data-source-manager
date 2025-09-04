from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.agency_identification.subtasks.planner.constants import SUBTASK_HIERARCHY
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.db.queries.base.builder import QueryBuilderBase


class AgencyIDSubtaskSurveyQueryBuilder(QueryBuilderBase):
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

    async def run(self, session: AsyncSession) -> list[AutoAgencyIDSubtaskType]:
        raise NotImplementedError



