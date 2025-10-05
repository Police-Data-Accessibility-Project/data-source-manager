from sqlalchemy import CTE, select, Column


class AgreementCTEContainer:

    def __init__(
        self,
        count_cte: CTE,
        agreed_cte: CTE,
        name: str
    ):
        self._cte = (
            select(
                count_cte.c.user_id,
                (agreed_cte.c.count / count_cte.c.count).label("agreement")
            )
            .join(
                agreed_cte,
                count_cte.c.user_id == agreed_cte.c.user_id
            )
            .cte(f"{name}_agreement")
        )

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def user_id(self) -> Column[int]:
        return self.cte.c.user_id

    @property
    def agreement(self) -> Column[float]:
        return self.cte.c.agreement

