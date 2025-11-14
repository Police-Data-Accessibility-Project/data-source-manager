from typing import Any

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.flag.ds_delete.data_source import FlagDSDeleteDataSource
from src.db.models.impl.flag.ds_delete.meta_url import FlagDSDeleteMetaURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL
from src.db.queries.base.builder import QueryBuilderBase


class DeleteURLQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int
    ):
        super().__init__()
        self.url_id = url_id

    async def run(self, session: AsyncSession) -> Any:

        await self._check_for_ds_app_link_data_source(session)
        await self._check_for_ds_app_link_meta_url(session)
        statement = (
            delete(
                URL
            ).where(
                URL.id == self.url_id
            )
        )
        await session.execute(statement)

    async def _check_for_ds_app_link_data_source(
        self,
        session: AsyncSession
    ) -> Any:
        """
        Check if a DS App Link Data Source exists for the URL
        If so, add a deletion flag
        """
        query = (
            select(DSAppLinkDataSource)
            .where(DSAppLinkDataSource.url_id == self.url_id)
        )
        ds_app_link_data_source: DSAppLinkDataSource | None = await self.sh.one_or_none(
            session=session,
            query=query
        )
        if ds_app_link_data_source is not None:
            delete_flag = FlagDSDeleteDataSource(
                ds_data_source_id=ds_app_link_data_source.ds_data_source_id
            )
            session.add(delete_flag)

    async def _check_for_ds_app_link_meta_url(
        self,
        session: AsyncSession
    ) -> Any:
        """
        Check if a DS App Link Meta URL exists for the URL
        If so, add a deletion flag
        """
        query = (
            select(DSAppLinkMetaURL)
            .where(DSAppLinkMetaURL.url_id == self.url_id)
        )
        ds_app_link_meta_url: DSAppLinkMetaURL | None = await self.sh.one_or_none(
            session=session,
            query=query
        )
        if ds_app_link_meta_url is not None:
            delete_flag = FlagDSDeleteMetaURL(
                ds_meta_url_id=ds_app_link_meta_url.ds_meta_url_id
            )
            session.add(delete_flag)

