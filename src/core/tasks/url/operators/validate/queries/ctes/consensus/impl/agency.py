from sqlalchemy import select, Column

from src.core.tasks.url.operators.validate.queries.ctes.consensus.base import ValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.helper import build_validation_query
from src.core.tasks.url.operators.validate.queries.ctes.counts.impl.agency import AGENCY_VALIDATION_COUNTS_CTE
from src.core.tasks.url.operators.validate.queries.ctes.scored import ScoredCTEContainer


class AgencyValidationCTEContainer(ValidationCTEContainer):

    def __init__(self):
        _scored = ScoredCTEContainer(
            AGENCY_VALIDATION_COUNTS_CTE
        )

        self._query = build_validation_query(
            _scored,
            "agency_id"
        )


    @property
    def agency_id(self) -> Column[int]:
        return self._query.c.agency_id