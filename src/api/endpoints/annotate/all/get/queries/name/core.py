from typing import Sequence

from sqlalchemy import select, func, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.get.models.name import NameAnnotationSuggestion
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.link.user_name_suggestion.sqlalchemy import LinkUserNameSuggestion
from src.db.models.impl.url.suggestion.name.sqlalchemy import URLNameSuggestion
from src.db.queries.base.builder import QueryBuilderBase


class GetNameSuggestionsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int
    ):
        super().__init__()
        self.url_id = url_id

    async def run(self, session: AsyncSession) -> list[NameAnnotationSuggestion]:
        query = (
            select(
                URLNameSuggestion.id.label('suggestion_id'),
                URLNameSuggestion.suggestion.label('name'),
                func.count(
                    LinkUserNameSuggestion.user_id
                ).label('endorsement_count'),
            )
            .outerjoin(
                LinkUserNameSuggestion,
                LinkUserNameSuggestion.suggestion_id == URLNameSuggestion.id,
            )
            .where(
                URLNameSuggestion.url_id == self.url_id,
            )
            .group_by(
                URLNameSuggestion.id,
                URLNameSuggestion.suggestion,
            )
            .order_by(
                func.count(LinkUserNameSuggestion.user_id).desc(),
                URLNameSuggestion.id.asc(),
            )
            .limit(3)
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        return [
            NameAnnotationSuggestion(
                **mapping
            )
            for mapping in mappings
        ]



