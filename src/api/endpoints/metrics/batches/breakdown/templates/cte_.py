from psycopg import Column
from sqlalchemy import CTE


class BatchesBreakdownURLCTE:

    def __init__(self, query: CTE):
        self._query = query

    @property
    def query(self) -> CTE:
        return self._query

    @property
    def batch_id(self) -> Column:
        return self._query.columns[0]

    @property
    def count(self) -> Column:
        return self._query.columns[1]