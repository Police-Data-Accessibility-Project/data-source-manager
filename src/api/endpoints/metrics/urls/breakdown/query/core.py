from sqlalchemy import select, case, literal, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.metrics.dtos.get.urls.breakdown.pending import GetMetricsURLsBreakdownPendingResponseInnerDTO, \
    GetMetricsURLsBreakdownPendingResponseDTO
from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.record_type.user.user import AnnotationRecordTypeUser
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationURLTypeUser
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetURLsBreakdownPendingMetricsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> GetMetricsURLsBreakdownPendingResponseDTO:

        flags = (
            select(
                URL.id.label("url_id"),
                case((AnnotationRecordTypeUser.url_id != None, literal(True)), else_=literal(False)).label(
                    "has_user_record_type_annotation"
                ),
                case((AnnotationURLTypeUser.url_id != None, literal(True)), else_=literal(False)).label(
                    "has_user_relevant_annotation"
                ),
                case((AnnotationAgencyUser.url_id != None, literal(True)), else_=literal(False)).label(
                    "has_user_agency_annotation"
                ),
            )
            .outerjoin(AnnotationRecordTypeUser, URL.id == AnnotationRecordTypeUser.url_id)
            .outerjoin(AnnotationURLTypeUser, URL.id == AnnotationURLTypeUser.url_id)
            .outerjoin(AnnotationAgencyUser, URL.id == AnnotationAgencyUser.url_id)
        ).cte("flags")

        month = func.date_trunc('month', URL.created_at)

        # Build the query
        query = (
            select(
                month.label('month'),
                func.count(URL.id).label('count_total'),
                func.count(
                    case(
                        (flags.c.has_user_record_type_annotation == True, 1)
                    )
                ).label('user_record_type_count'),
                func.count(
                    case(
                        (flags.c.has_user_relevant_annotation == True, 1)
                    )
                ).label('user_relevant_count'),
                func.count(
                    case(
                        (flags.c.has_user_agency_annotation == True, 1)
                    )
                ).label('user_agency_count'),
            )
            .outerjoin(flags, flags.c.url_id == URL.id)
            .outerjoin(
                FlagURLValidated,
                FlagURLValidated.url_id == URL.id
            )
            .where(
                FlagURLValidated.url_id.is_(None)
            )
            .group_by(month)
            .order_by(month.asc())
        )

        # Execute the query and return the results
        results = await session.execute(query)
        all_results = results.all()
        final_results: list[GetMetricsURLsBreakdownPendingResponseInnerDTO] = []

        for result in all_results:
            dto = GetMetricsURLsBreakdownPendingResponseInnerDTO(
                month=result.month.strftime("%B %Y"),
                count_pending_total=result.count_total,
                count_pending_relevant_user=result.user_relevant_count,
                count_pending_record_type_user=result.user_record_type_count,
                count_pending_agency_user=result.user_agency_count,
            )
            final_results.append(dto)
        return GetMetricsURLsBreakdownPendingResponseDTO(
            entries=final_results,
        )