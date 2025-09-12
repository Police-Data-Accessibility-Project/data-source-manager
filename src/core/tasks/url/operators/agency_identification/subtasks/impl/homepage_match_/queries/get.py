from typing import Sequence

from sqlalchemy import Select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.models.entry import \
    GetHomepageMatchParams
from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.queries.ctes.multi_agency_case import \
    MULTI_AGENCY_CASE_QUERY
from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.queries.ctes.single_agency_case import \
    SINGLE_AGENCY_CASE_QUERY
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.url.suggestion.agency.subtask.enum import SubtaskDetailCode
from src.db.queries.base.builder import QueryBuilderBase


class GetHomepageMatchSubtaskURLsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[GetHomepageMatchParams]:

        query: Select = SINGLE_AGENCY_CASE_QUERY.union(MULTI_AGENCY_CASE_QUERY)

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)

        results: list[GetHomepageMatchParams] = []
        for mapping in mappings:
            response = GetHomepageMatchParams(
                url_id=mapping["url_id"],
                agency_id=mapping["agency_id"],
                confidence=mapping["confidence"],
                detail_code=SubtaskDetailCode(mapping["detail_code"]),
            )
            results.append(response)

        return results