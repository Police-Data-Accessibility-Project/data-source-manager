from sqlalchemy import Column

from src.core.tasks.url.operators.validate.queries.ctes.consensus.base import ValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.helper import build_validation_query
from src.core.tasks.url.operators.validate.queries.ctes.counts.impl.location import LOCATION_VALIDATION_COUNTS_CTE
from src.core.tasks.url.operators.validate.queries.ctes.scored import ScoredCTEContainer


class LocationValidationCTEContainer(ValidationCTEContainer):

    def __init__(self):
        _scored = ScoredCTEContainer(
            LOCATION_VALIDATION_COUNTS_CTE
        )

        self._query = build_validation_query(
            _scored,
            "location_id"
        )

    @property
    def location_id(self) -> Column[int]:
        return self._query.c.location_id