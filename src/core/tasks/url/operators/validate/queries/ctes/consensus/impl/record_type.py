from sqlalchemy import select, Column

from src.core.tasks.url.operators.validate.queries.ctes.consensus.base import ValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.counts.impl.record_type import RECORD_TYPE_COUNTS_CTE
from src.core.tasks.url.operators.validate.queries.ctes.scored import ScoredCTEContainer


class RecordTypeValidationCTEContainer(ValidationCTEContainer):

    def __init__(self):

        _scored = ScoredCTEContainer(
            RECORD_TYPE_COUNTS_CTE
        )

        self._query = (
            select(
                _scored.url_id,
                _scored.entity.label("record_type")
            )
            .where(
                _scored.rnk == 1,
                _scored.max_votes >= 2,
                _scored.num_labels_with_that_vote == 1
            )
            .cte("record_type_validation")
        )

    @property
    def record_type(self) -> Column[str]:
        return self._query.c.record_type