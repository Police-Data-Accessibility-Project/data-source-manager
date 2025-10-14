from sqlalchemy import select

from src.core.tasks.url.operators._shared.container.subtask.exists import \
    URLsSubtaskExistsCTEContainer
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.location.auto.subtask.sqlalchemy import AutoLocationIDSubtask
from src.db.models.impl.url.suggestion.location.auto.suggestion.sqlalchemy import LocationIDSubtaskSuggestion

cte = (
    select(
        URL.id
    )
    .join(
        AutoLocationIDSubtask,
        AutoLocationIDSubtask.url_id == URL.id,
    )
    .join(
        LocationIDSubtaskSuggestion,
        LocationIDSubtaskSuggestion.subtask_id == AutoLocationIDSubtask.id,
    )
    .where(
        LocationIDSubtaskSuggestion.confidence >= 95,
    )
    .cte("high_confidence_annotations_exists")
)

HIGH_CONFIDENCE_ANNOTATIONS_EXISTS_CONTAINER = URLsSubtaskExistsCTEContainer(
    cte,
)