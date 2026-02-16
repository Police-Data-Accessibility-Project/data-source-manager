from sqlalchemy import select, literal

from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.queries.ctes.consolidated import \
    CONSOLIDATED_CTE
from src.db.models.impl.annotation.agency.auto.subtask.enum import SubtaskDetailCode

MULTI_AGENCY_CASE_QUERY = (
    select(
        CONSOLIDATED_CTE.c.url_id,
        CONSOLIDATED_CTE.c.agency_id,
        (literal(100) / CONSOLIDATED_CTE.c.agency_count).label("confidence"),
        literal(SubtaskDetailCode.HOMEPAGE_MULTI_AGENCY.value).label("detail_code")
    )
    .where(
        CONSOLIDATED_CTE.c.agency_count > 1
    )
)