from sqlalchemy import CTE, Column


class ValidatedCountsCTEContainer:

    def __init__(self, cte: CTE):
        self._cte: CTE = cte

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def url_id(self) -> Column[int]:
        return self._cte.c.url_id

    @property
    def entity(self) -> Column:
        return self._cte.c.entity

    @property
    def votes(self) -> Column[int]:
        return self._cte.c.votes