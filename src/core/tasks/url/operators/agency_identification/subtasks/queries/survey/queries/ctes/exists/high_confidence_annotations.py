from sqlalchemy import select

from src.core.tasks.url.operators._shared.container.subtask.exists import \
    URLsSubtaskExistsCTEContainer
from src.db.models.impl.annotation.agency.auto.subtask.sqlalchemy import AnnotationAgencyAutoSubtask
from src.db.models.impl.annotation.agency.auto.suggestion.sqlalchemy import AnnotationAgencyAutoSuggestion
from src.db.models.impl.url.core.sqlalchemy import URL

cte = (
    select(
        URL.id
    )
    .join(
        AnnotationAgencyAutoSubtask,
        AnnotationAgencyAutoSubtask.url_id == URL.id,
    )
    .join(
        AnnotationAgencyAutoSuggestion,
        AnnotationAgencyAutoSuggestion.subtask_id == AnnotationAgencyAutoSubtask.id,
    )
    .where(
        AnnotationAgencyAutoSuggestion.confidence >= 95,
    )
    .cte("high_confidence_annotations_exists")
)

HIGH_CONFIDENCE_ANNOTATIONS_EXISTS_CONTAINER = URLsSubtaskExistsCTEContainer(
    cte,
)