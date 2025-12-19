from sqlalchemy import select

from src.core.tasks.url.operators._shared.container.subtask.exists import \
    URLsSubtaskExistsCTEContainer
from src.db.models.impl.annotation.location.auto.subtask.sqlalchemy import AnnotationLocationAutoSubtask
from src.db.models.impl.annotation.location.auto.suggestion.sqlalchemy import AnnotationLocationAutoSuggestion
from src.db.models.impl.url.core.sqlalchemy import URL

cte = (
    select(
        URL.id
    )
    .join(
        AnnotationLocationAutoSubtask,
        AnnotationLocationAutoSubtask.url_id == URL.id,
    )
    .join(
        AnnotationLocationAutoSuggestion,
        AnnotationLocationAutoSuggestion.subtask_id == AnnotationLocationAutoSubtask.id,
    )
    .where(
        AnnotationLocationAutoSuggestion.confidence >= 95,
    )
    .cte("high_confidence_annotations_exists")
)

HIGH_CONFIDENCE_ANNOTATIONS_EXISTS_CONTAINER = URLsSubtaskExistsCTEContainer(
    cte,
)