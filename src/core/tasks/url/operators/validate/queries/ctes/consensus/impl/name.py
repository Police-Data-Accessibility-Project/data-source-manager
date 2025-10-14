from sqlalchemy import Column

from src.core.tasks.url.operators.validate.queries.ctes.consensus.base import ValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.helper import build_validation_query
from src.core.tasks.url.operators.validate.queries.ctes.counts.impl.name import NAME_VALIDATION_COUNTS_CTE
from src.core.tasks.url.operators.validate.queries.ctes.scored import ScoredCTEContainer


class NameValidationCTEContainer(ValidationCTEContainer):

    def __init__(self):
        _scored = ScoredCTEContainer(
            NAME_VALIDATION_COUNTS_CTE
        )

        self._query = build_validation_query(
            _scored,
            "name"
        )

    @property
    def name(self) -> Column[int]:
        return self._query.c.name