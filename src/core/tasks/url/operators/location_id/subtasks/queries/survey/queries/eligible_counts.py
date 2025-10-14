from sqlalchemy import ColumnElement, func, Integer, select

from src.core.tasks.url.operators.location_id.subtasks.queries.survey.queries.ctes.eligible import EligibleContainer
from src.db.models.impl.url.suggestion.location.auto.subtask.enums import LocationIDSubtaskType


def sum_count(col: ColumnElement[bool], subtask_type: LocationIDSubtaskType) -> ColumnElement[int]:
    return func.coalesce(
        func.sum(
            col.cast(Integer)
        ),
        0,
    ).label(subtask_type.value)

container = EligibleContainer()

ELIGIBLE_COUNTS_QUERY = (
    select(
        sum_count(container.nlp_location, LocationIDSubtaskType.NLP_LOCATION_FREQUENCY),
        sum_count(container.batch_link, LocationIDSubtaskType.BATCH_LINK)
    )
)