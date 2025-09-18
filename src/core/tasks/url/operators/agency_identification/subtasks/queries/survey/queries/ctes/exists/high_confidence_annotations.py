from sqlalchemy import select

from src.core.tasks.url.operators._shared.container.subtask.exists import \
    URLsSubtaskExistsCTEContainer
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask
from src.db.models.impl.url.suggestion.agency.suggestion.sqlalchemy import AgencyIDSubtaskSuggestion

cte = (
    select(
        URL.id
    )
    .join(
        URLAutoAgencyIDSubtask,
        URLAutoAgencyIDSubtask.url_id == URL.id,
    )
    .join(
        AgencyIDSubtaskSuggestion,
        AgencyIDSubtaskSuggestion.subtask_id == URLAutoAgencyIDSubtask.id,
    )
    .where(
        AgencyIDSubtaskSuggestion.confidence >= 95,
    )
    .cte("high_confidence_annotations_exists")
)

HIGH_CONFIDENCE_ANNOTATIONS_EXISTS_CONTAINER = URLsSubtaskExistsCTEContainer(
    cte,
)