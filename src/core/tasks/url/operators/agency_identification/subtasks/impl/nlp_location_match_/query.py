from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.models.input import \
    NLPLocationMatchSubtaskInput
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.queries.base.builder import QueryBuilderBase


class GetNLPLocationMatchSubtaskInputQueryBuilder(QueryBuilderBase):

    async def run(
        self,
        session: AsyncSession
    ) -> list[NLPLocationMatchSubtaskInput]:

        query = (
            select(
                URL.id,
                URLCompressedHTML.compressed_html
            )
            .join(
                URLCompressedHTML,
                URLCompressedHTML.url_id == URL.id
            )
        )

        # TODO: Add additional joins and where conditions
        # TODO: Maybe leverage CTEs from survey query to get the precise URL ids
        #  without having to redo the logic here


        # TODO: Add limit leveraging NUMBER_OF_ENTRIES_PER_ITERATION constant
