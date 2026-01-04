from operator import and_

from sqlalchemy import select, exists

from src.core.tasks.url.operators._shared.container.subtask.eligible import URLsSubtaskEligibleCTEContainer
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.helpers import \
    get_exists_subtask_query
from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.annotation.location.auto.subtask.sqlalchemy import AnnotationLocationAutoSubtask
from src.db.models.impl.annotation.location.auto.suggestion.sqlalchemy import AnnotationLocationAutoSuggestion
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.models.impl.url.core.sqlalchemy import URL

cte = (
    select(
        URL.id,
        get_exists_subtask_query(
            AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH
        )
    )
    .join(
        AnnotationLocationAutoSubtask,
        and_(
            AnnotationLocationAutoSubtask.url_id == URL.id,
            AnnotationLocationAutoSubtask.locations_found
        )
    )
    .where(
        # One of the locations must be linked to an agency
        exists(
            select(
                LinkAgencyLocation.location_id
            )
            .join(
                AnnotationLocationAutoSuggestion,
                AnnotationLocationAutoSuggestion.location_id == LinkAgencyLocation.location_id,
            )
            .join(
                AnnotationLocationAutoSubtask,
                AnnotationLocationAutoSubtask.id == AnnotationLocationAutoSuggestion.subtask_id,
            )
        )

    )
    .cte("nlp_location_eligible")
)

NLP_LOCATION_CONTAINER = URLsSubtaskEligibleCTEContainer(
    cte,
)