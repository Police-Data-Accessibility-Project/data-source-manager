from sqlalchemy import select, Column

from src.core.tasks.url.operators.validate.queries.ctes.consensus.base import ValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.helper import build_validation_query
from src.core.tasks.url.operators.validate.queries.ctes.counts.impl.record_type import RECORD_TYPE_COUNTS_CTE
from src.core.tasks.url.operators.validate.queries.ctes.scored import ScoredCTEContainer


class RecordTypeValidationCTEContainer(ValidationCTEContainer):

    def __init__(self):

        _scored = ScoredCTEContainer(
            RECORD_TYPE_COUNTS_CTE
        )

        self._query = build_validation_query(
            _scored,
            "record_type"
        )

    @property
    def record_type(self) -> Column[str]:
        return self._query.c.record_type