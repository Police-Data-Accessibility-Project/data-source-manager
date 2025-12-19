from typing import Sequence

from sqlalchemy import select, func, RowMapping, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.get.models.name import NameAnnotationSuggestion, NameAnnotationResponseOuterInfo
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.annotation.name.suggestion.enums import NameSuggestionSource
from src.db.models.impl.annotation.name.suggestion.sqlalchemy import AnnotationNameSuggestion
from src.db.models.impl.annotation.name.user.sqlalchemy import LinkUserNameSuggestion
from src.db.queries.base.builder import QueryBuilderBase


class GetNameSuggestionsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int
    ):
        super().__init__()
        self.url_id = url_id

    async def run(self, session: AsyncSession) -> NameAnnotationResponseOuterInfo:
        query = (
            select(
                AnnotationNameSuggestion.id.label('id'),
                AnnotationNameSuggestion.suggestion.label('display_name'),
                func.count(
                    LinkUserNameSuggestion.user_id
                ).label('user_count'),
                case(
                    (AnnotationNameSuggestion.source == NameSuggestionSource.HTML_METADATA_TITLE, 1),
                    else_=0
                ).label("robo_count")
            )
            .outerjoin(
                LinkUserNameSuggestion,
                LinkUserNameSuggestion.suggestion_id == AnnotationNameSuggestion.id,
            )
            .where(
                AnnotationNameSuggestion.url_id == self.url_id,
            )
            .group_by(
                AnnotationNameSuggestion.id,
                AnnotationNameSuggestion.suggestion,
            )
            .order_by(
                func.count(LinkUserNameSuggestion.user_id).desc(),
                AnnotationNameSuggestion.id.asc(),
            )
            .limit(3)
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        suggestions = [
            NameAnnotationSuggestion(
                **mapping
            )
            for mapping in mappings
        ]
        return NameAnnotationResponseOuterInfo(
            suggestions=suggestions
        )



