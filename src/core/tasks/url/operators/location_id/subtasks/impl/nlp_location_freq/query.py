from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.constants import \
    NUMBER_OF_ENTRIES_PER_ITERATION
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.models.input import \
    NLPLocationMatchSubtaskInput
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.eligible import \
    EligibleContainer
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.suggestion.location.auto.subtask.sqlalchemy import AutoLocationIDSubtask
from src.db.models.impl.url.suggestion.location.auto.suggestion.sqlalchemy import LocationIDSubtaskSuggestion
from src.db.queries.base.builder import QueryBuilderBase
from src.db.utils.compression import decompress_html


class GetNLPLocationMatchSubtaskInputQueryBuilder(QueryBuilderBase):

    # TODO: Change
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
                AutoLocationIDSubtask,
                AutoLocationIDSubtask.url_id == container.url_id,
            )
            .join(
                LocationIDSubtaskSuggestion,
                LocationIDSubtaskSuggestion.subtask_id == AutoLocationIDSubtask.id
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

