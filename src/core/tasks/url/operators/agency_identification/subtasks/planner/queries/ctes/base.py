from sqlalchemy import CTE, Column


class PrereqCTE:
    """
    Base class for CTEs that determine validity for each subtask.

    Single column CTEs intended to be left-joined and considered valid only
    if the joined row is not null.
    """

    def __init__(
        self,
        cte: CTE
    ) -> None:
        self._cte = cte

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def url_id(self) -> Column[int]:
        return self.cte.columns[0]