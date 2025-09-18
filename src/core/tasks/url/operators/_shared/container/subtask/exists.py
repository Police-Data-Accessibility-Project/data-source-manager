from sqlalchemy import CTE, Column, ColumnElement, exists

from src.db.models.impl.url.core.sqlalchemy import URL


class URLsSubtaskExistsCTEContainer:
    """
    Base class for CTEs that determine validity for each subtask.

    Single column CTEs intended to be left-joined and considered valid only
    if the joined row is not null.
    """

    def __init__(
        self,
        cte: CTE,
    ) -> None:
        self._cte = cte

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def url_id(self) -> Column[int]:
        return self.cte.columns[0]

    @property
    def not_exists_query(self) -> ColumnElement[bool]:
        return (
            ~exists()
            .where(self.url_id == URL.id)
        )