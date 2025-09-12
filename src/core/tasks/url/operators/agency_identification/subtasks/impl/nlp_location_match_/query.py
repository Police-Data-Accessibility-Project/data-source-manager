from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.constants import \
    NUMBER_OF_ENTRIES_PER_ITERATION
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.models.input import \
    NLPLocationMatchSubtaskInput
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.eligible import \
    EligibleContainer
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.queries.base.builder import QueryBuilderBase
from src.db.utils.compression import decompress_html


class GetNLPLocationMatchSubtaskInputQueryBuilder(QueryBuilderBase):

    async def run(
        self,
        session: AsyncSession
    ) -> list[NLPLocationMatchSubtaskInput]:
        container = EligibleContainer()
        query = (
            select(
                container.url_id,
                URLCompressedHTML.compressed_html
            )
            .join(
                URLCompressedHTML,
                URLCompressedHTML.url_id == container.url_id,
            )
            .where(
                container.nlp_location,
            )
            .limit(NUMBER_OF_ENTRIES_PER_ITERATION)
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        inputs: list[NLPLocationMatchSubtaskInput] = [
            NLPLocationMatchSubtaskInput(
                url_id=mapping["id"],
                html=decompress_html(mapping["compressed_html"]),
            )
            for mapping in mappings
        ]
        return inputs

