from sqlalchemy import select, Column, CTE

from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.suggestion.relevant.user import UserURLTypeSuggestion


class AnnotatedAndValidatedCTEContainer:

    def __init__(self, user_id: int | None):
        self._cte = (
            select(
                UserURLTypeSuggestion.user_id,
                UserURLTypeSuggestion.url_id
            )
            .join(
                FlagURLValidated,
                FlagURLValidated.url_id == UserURLTypeSuggestion.url_id
            )
        )
        if user_id is not None:
            self._cte = self._cte.where(UserURLTypeSuggestion.user_id == user_id)
        self._cte = self._cte.cte("annotated_and_validated")

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def url_id(self) -> Column[int]:
        return self.cte.c.url_id

    @property
    def user_id(self) -> Column[int]:
        return self.cte.c.user_id