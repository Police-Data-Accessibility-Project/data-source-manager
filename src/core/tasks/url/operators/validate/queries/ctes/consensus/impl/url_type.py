from sqlalchemy import select, Column

from src.core.tasks.url.operators.validate.queries.ctes.consensus.base import ValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.counts.impl.url_type import URL_TYPES_VALIDATION_COUNTS_CTE
from src.core.tasks.url.operators.validate.queries.ctes.scored import ScoredCTEContainer


class URLTypeValidationCTEContainer(ValidationCTEContainer):

    def __init__(self):
        _scored = ScoredCTEContainer(
            URL_TYPES_VALIDATION_COUNTS_CTE
        )

        self._query = (
            select(
                _scored.url_id,
                _scored.entity.label("url_type")
            )
            .where(
                _scored.rnk == 1,
                _scored.max_votes >= 2,
                _scored.num_labels_with_that_vote == 1
            )
            .cte("url_type_validation")
        )

    @property
    def url_type(self) -> Column[str]:
        return self._query.c.url_type