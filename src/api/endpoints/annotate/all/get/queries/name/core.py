from typing import Sequence

from sqlalchemy import select, func, RowMapping, case
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.get.models.name import NameAnnotationSuggestion, NameAnnotationResponseOuterInfo
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.annotation.name.anon.sqlalchemy import AnnotationNameAnonEndorsement
from src.db.models.impl.annotation.name.suggestion.enums import NameSuggestionSource
from src.db.models.impl.annotation.name.suggestion.sqlalchemy import AnnotationNameSuggestion
from src.db.models.impl.annotation.name.user.sqlalchemy import AnnotationNameUserEndorsement
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
                    AnnotationNameUserEndorsement.user_id
                ).label('user_count'),
                func.count(
                    AnnotationNameAnonEndorsement.session_id
                ).label('anon_count'),
                case(
                    (AnnotationNameSuggestion.source == NameSuggestionSource.HTML_METADATA_TITLE, 1),
                    else_=0
                ).label("robo_count")
            )
            .outerjoin(
                AnnotationNameUserEndorsement,
                AnnotationNameUserEndorsement.suggestion_id == AnnotationNameSuggestion.id,
            )
            .outerjoin(
                AnnotationNameAnonEndorsement,
                AnnotationNameAnonEndorsement.suggestion_id == AnnotationNameSuggestion.id,
            )
            .where(
                AnnotationNameSuggestion.url_id == self.url_id,
            )
            .group_by(
                AnnotationNameSuggestion.id,
                AnnotationNameSuggestion.suggestion,
            )
            .order_by(
                (func.count(AnnotationNameUserEndorsement.user_id) + func.count(
                    AnnotationNameUserEndorsement.user_id
                )).desc(),
                AnnotationNameSuggestion.id.asc(),
            )
            .limit(3)
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        suggestions = [
            NameAnnotationSuggestion(
                id=mapping["id"],
                display_name=mapping["display_name"],
                user_count=mapping['user_count'] + (mapping['anon_count'] // 2),
                robo_count=mapping["robo_count"]
            )
            for mapping in mappings
        ]
        return NameAnnotationResponseOuterInfo(
            suggestions=suggestions
        )



