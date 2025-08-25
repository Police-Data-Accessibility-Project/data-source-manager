from sqlalchemy import CTE, Column


class URLCountsCTEContainer:

    def __init__(
        self,
        cte: CTE
    ):
        self.cte = cte

    @property
    def batch_id(self) -> Column:
        return self.cte.columns[0]

    @property
    def count(self) -> Column:
        return self.cte.columns[1]
