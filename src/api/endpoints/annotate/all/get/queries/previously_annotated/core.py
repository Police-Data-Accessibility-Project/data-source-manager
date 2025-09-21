from sqlalchemy import CTE
from sqlalchemy.orm import InstrumentedAttribute

from src.api.endpoints.annotate.all.get.queries.previously_annotated.build import build_cte


class URLPreviouslyAnnotatedByUserCTEContainer:

    def __init__(
        self,
        user_id: int
    ):
        self.user_id = user_id
        self._cte: CTE = build_cte(user_id=user_id)

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def url_id(self) -> InstrumentedAttribute[int]:
        return self._cte.c.id