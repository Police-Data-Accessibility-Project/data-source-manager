from sqlalchemy import select, ColumnElement, Integer, func

from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.eligible import ELIGIBLE_CTE
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType


def sum_count(col: ColumnElement[bool], subtask_type: AutoAgencyIDSubtaskType) -> ColumnElement[int]:
    return func.coalesce(
        func.sum(
            col.cast(Integer)
        ),
        0,
    ).label(subtask_type.value)

ELIGIBLE_COUNTS_QUERY = (
    select(
        sum_count(ELIGIBLE_CTE.c.ckan, AutoAgencyIDSubtaskType.CKAN),
        sum_count(ELIGIBLE_CTE.c.muckrock, AutoAgencyIDSubtaskType.MUCKROCK),
        sum_count(ELIGIBLE_CTE.c.homepage, AutoAgencyIDSubtaskType.HOMEPAGE_MATCH),
        sum_count(ELIGIBLE_CTE.c.nlp_location, AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH),
    )
)