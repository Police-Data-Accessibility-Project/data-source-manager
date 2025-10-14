from sqlalchemy import select

from src.core.tasks.url.operators._shared.container.subtask.exists import \
    URLsSubtaskExistsCTEContainer
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated

cte = (
    select(
        FlagURLValidated.url_id
    )
    .cte("validated_exists")
)

VALIDATED_EXISTS_CONTAINER = URLsSubtaskExistsCTEContainer(
    cte,
)