from sqlalchemy import CTE, Column


class CountCTE:

    def __init__(self, cte: CTE):
        self.cte = cte

    @property
    def batch_id(self) -> Column[int]:
        return self.cte.c['batch_id']

    @property
    def count(self) -> Column[int]:
        return self.cte.c['count']