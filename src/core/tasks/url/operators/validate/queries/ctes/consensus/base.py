from abc import ABC, abstractmethod

from sqlalchemy import Column, CTE


class ValidationCTEContainer:
    _query: CTE

    @property
    def url_id(self) -> Column[int]:
        return self._query.c.url_id

    @property
    def query(self) -> CTE:
        return self._query