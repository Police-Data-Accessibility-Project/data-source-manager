from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.submit.data_source.models.response.duplicate import \
    SubmitDataSourceURLDuplicateSubmissionResponse
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.materialized_views.url_status.sqlalchemy import URLStatusMaterializedView
from src.db.queries.base.builder import QueryBuilderBase


class GetDataSourceDuplicateQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url: str
    ):
        super().__init__()
        self.url = url

    async def run(self, session: AsyncSession) -> None:
        """
        Raises:
            HTTPException including details on the duplicate result.
        """

        query = (
            select(
                URL.id,
                URLStatusMaterializedView.status,
                FlagURLValidated.type
            )
            .outerjoin(
                FlagURLValidated,
                FlagURLValidated.url_id == URL.id
            )
            .outerjoin(
                URLStatusMaterializedView.status
            )
            .where(
                URL.url == self.url
            )
        )
        mapping: RowMapping = await self.sh.mapping(
            query=query,
            session=session
        )

        model = SubmitDataSourceURLDuplicateSubmissionResponse(
            message="Duplicate URL found",
            url_id=mapping[URL.id],
            url_status=mapping[URLStatusMaterializedView.status],
            url_type=mapping[FlagURLValidated.type]
        )
        raise HTTPException(
            detail=model.model_dump(mode='json'),
            status_code=HTTPStatus.CONFLICT
        )

