from sqlalchemy import select

from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.exists.container import \
    ExistsCTEContainer
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated

cte = (
    select(
        FlagURLValidated.url_id
    )
    .cte("validated_exists")
)

VALIDATED_EXISTS_CONTAINER = ExistsCTEContainer(
    cte,
)