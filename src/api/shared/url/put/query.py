from typing import Any

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.util.models.full_url import FullURL


class UpdateURLQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int,
        url: str | None,
        name: str | None,
        description: str | None
    ):
        super().__init__()
        self.url_id = url_id
        self.url = url
        self.name = name
        self.description = description

    async def run(self, session: AsyncSession) -> Any:
        values_dict = {}
        if self.url is not None:
            full_url = FullURL(self.url)
            values_dict["url"] = full_url.id_form
            values_dict["scheme"] = full_url.scheme
            values_dict["trailing_slash"] = full_url.has_trailing_slash
        if self.name is not None:
            values_dict["name"] = self.name
        if self.description is not None:
            values_dict["description"] = self.description

        query = (
            update(
                URL
            )
            .where(
                URL.id == self.url_id
            )
            .values(
                values_dict
            )
        )

        await session.execute(query)