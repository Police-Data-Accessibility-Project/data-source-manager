from sqlalchemy import CTE, ColumnElement, Column, Select, exists, func

from src.db.models.impl.url.core.sqlalchemy import URL


class URLsSubtaskEligibleCTEContainer:
    """
    CTE for URLs eligible for a given subtask.
    A successful left join on this indicates the URL is eligible for the subtask.
    A true value for `subtask_entry_exists` indicates
        a subtask entry for the URL already exists
    """

    def __init__(
        self,
        cte: CTE,
    ) -> None:
        self._cte=cte

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def entry_exists(self) -> ColumnElement[bool]:
        return self.cte.c['subtask_entry_exists']

    @property
    def url_id(self) -> Column[int]:
        return self.cte.c['id']

    @property
    def eligible_query(self) -> ColumnElement[bool]:
        return (
            exists()
            .where(
                self.url_id == URL.id,
                self.entry_exists.is_(False),
            )
        )