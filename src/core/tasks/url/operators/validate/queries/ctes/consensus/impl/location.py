from sqlalchemy import select, Column

from src.core.tasks.url.operators.validate.queries.ctes.consensus.base import ValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.counts.impl.location import LOCATION_VALIDATION_COUNTS_CTE
from src.core.tasks.url.operators.validate.queries.ctes.scored import ScoredCTEContainer


class LocationValidationCTEContainer(ValidationCTEContainer):

    def __init__(self):
        _scored = ScoredCTEContainer(
            LOCATION_VALIDATION_COUNTS_CTE
        )

        self._query = (
            select(
                _scored.url_id,
                _scored.entity.label("location_id")
            )
            .where(
                _scored.rnk == 1,
                _scored.max_votes >= 2,
                _scored.num_labels_with_that_vote == 1
            )
            .cte("location_validation")
        )

    @property
    def location_id(self) -> Column[int]:
        return self._query.c.location_id