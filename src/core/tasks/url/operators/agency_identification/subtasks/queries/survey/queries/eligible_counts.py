from sqlalchemy import select, ColumnElement, Integer, func

from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.eligible import \
    EligibleContainer
from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType


def sum_count(col: ColumnElement[bool], subtask_type: AutoAgencyIDSubtaskType) -> ColumnElement[int]:
    return func.coalesce(
        func.sum(
            col.cast(Integer)
        ),
        0,
    ).label(subtask_type.value)

container = EligibleContainer()

ELIGIBLE_COUNTS_QUERY = (
    select(
        sum_count(container.ckan, AutoAgencyIDSubtaskType.CKAN),
        sum_count(container.muckrock, AutoAgencyIDSubtaskType.MUCKROCK),
        sum_count(container.homepage, AutoAgencyIDSubtaskType.HOMEPAGE_MATCH),
        sum_count(container.nlp_location, AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH),
        sum_count(container.batch_link, AutoAgencyIDSubtaskType.BATCH_LINK)
    )
)