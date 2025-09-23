from sqlalchemy import select, Column

from src.core.tasks.url.operators.validate.queries.ctes.consensus.base import ValidationCTEContainer
from src.core.tasks.url.operators.validate.queries.ctes.consensus.helper import build_validation_query
from src.core.tasks.url.operators.validate.queries.ctes.counts.impl.url_type import URL_TYPES_VALIDATION_COUNTS_CTE
from src.core.tasks.url.operators.validate.queries.ctes.scored import ScoredCTEContainer


class URLTypeValidationCTEContainer(ValidationCTEContainer):

    def __init__(self):
        _scored = ScoredCTEContainer(
            URL_TYPES_VALIDATION_COUNTS_CTE
        )

        self._query = build_validation_query(
            _scored,
            "url_type"
        )

    @property
    def url_type(self) -> Column[str]:
        return self._query.c.url_type