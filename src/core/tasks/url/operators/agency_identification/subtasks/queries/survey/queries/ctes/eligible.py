from sqlalchemy import select, CTE, Column

from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.exists.high_confidence_annotations import \
    HIGH_CONFIDENCE_ANNOTATIONS_EXISTS_CONTAINER
from src.core.tasks.url.operators._shared.ctes.validated import \
    VALIDATED_EXISTS_CONTAINER
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.impl.batch_link import \
    BATCH_LINK_SUBTASK_CONTAINER
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.impl.ckan import \
    CKAN_SUBTASK_CONTAINER
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.impl.homepage import \
    HOMEPAGE_SUBTASK_CONTAINER
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.impl.muckrock import \
    MUCKROCK_SUBTASK_CONTAINER
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.impl.nlp_location import \
    NLP_LOCATION_CONTAINER
from src.db.models.impl.url.core.sqlalchemy import URL

class EligibleContainer:

    def __init__(self):
        self._cte = (
            select(
                URL.id,
                CKAN_SUBTASK_CONTAINER.eligible_query.label("ckan"),
                MUCKROCK_SUBTASK_CONTAINER.eligible_query.label("muckrock"),
                HOMEPAGE_SUBTASK_CONTAINER.eligible_query.label("homepage"),
                NLP_LOCATION_CONTAINER.eligible_query.label("nlp_location"),
                BATCH_LINK_SUBTASK_CONTAINER.eligible_query.label("batch_link"),
            )
            .where(
                HIGH_CONFIDENCE_ANNOTATIONS_EXISTS_CONTAINER.not_exists_query,
                VALIDATED_EXISTS_CONTAINER.not_exists_query,
            )
            .cte("eligible")
        )

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def url_id(self) -> Column[int]:
        return self._cte.c['id']

    @property
    def ckan(self) -> Column[bool]:
        return self._cte.c['ckan']

    @property
    def batch_link(self) -> Column[bool]:
        return self._cte.c['batch_link']

    @property
    def muckrock(self) -> Column[bool]:
        return self._cte.c['muckrock']

    @property
    def homepage(self) -> Column[bool]:
        return self._cte.c['homepage']

    @property
    def nlp_location(self) -> Column[bool]:
        return self._cte.c['nlp_location']