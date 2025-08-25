from typing import final

from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override

from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.convert import convert_url_sync_info_to_url_mappings
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.helpers.filter import filter_for_urls_with_ids, \
    get_mappings_for_urls_without_data_sources
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.mapper import URLSyncInfoMapper
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.param_manager import \
    UpsertURLsFromDataSourcesParamManager
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.requester import UpsertURLsFromDataSourcesDBRequester
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.url.insert.params import \
    InsertURLForDataSourcesSyncParams
from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.url.lookup.response import \
    LookupURLForDataSourcesSyncResponse
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.flag.url_validated.pydantic import FlagURLValidatedPydantic
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInnerInfo
from src.util.url_mapper import URLMapper


@final
class UpsertURLsFromDataSourcesQueryBuilder(QueryBuilderBase):

    def __init__(self, sync_infos: list[DataSourcesSyncResponseInnerInfo]):
        super().__init__()
        self.sync_infos = sync_infos
        self.urls = {sync_info.url for sync_info in self.sync_infos}
        self.param_manager = UpsertURLsFromDataSourcesParamManager(
            mapper=URLSyncInfoMapper(self.sync_infos)
        )
        self._session: AsyncSession | None = None
        self._requester: UpsertURLsFromDataSourcesDBRequester | None = None
        # Need to be able to add URL ids first before adding links or other attributes

    @property
    def requester(self) -> UpsertURLsFromDataSourcesDBRequester:
        """
        Modifies:
            self._requester
        """
        if self._requester is None:
            self._requester = UpsertURLsFromDataSourcesDBRequester(self._session)
        return self._requester

    @override
    async def run(self, session: AsyncSession) -> None:
        """
        Modifies:
            self._session
        """
        self._session = session

        lookup_results: list[LookupURLForDataSourcesSyncResponse] = await self._lookup_urls()

        # Update existing url and associated metadata
        lookups_existing_urls: list[LookupURLForDataSourcesSyncResponse] = filter_for_urls_with_ids(lookup_results)
        await self._update_existing_urls(lookups_existing_urls)
        await self._update_agency_link(lookups_existing_urls)
        existing_url_mappings: list[URLMapping] = [
            convert_url_sync_info_to_url_mappings(lookup.url_info)
            for lookup in lookups_existing_urls
        ]

        # Add new URLs and associated metadata
        mappings_without_data_sources: list[URLMapping] = get_mappings_for_urls_without_data_sources(lookup_results)
        await self._add_new_data_sources(mappings_without_data_sources)
        extant_urls: set[str] = {lookup.url_info.url for lookup in lookups_existing_urls}
        urls_to_add: list[str] = list(self.urls - extant_urls)
        if len(urls_to_add) != 0:
            new_url_mappings: list[URLMapping] = await self._add_new_urls(urls_to_add)
            await self._add_new_data_sources(new_url_mappings)
            await self._insert_agency_link(new_url_mappings)
        else:
            new_url_mappings: list[URLMapping] = []

        # Upsert validated flags
        all_url_mappings: list[URLMapping] = existing_url_mappings + new_url_mappings
        mapper = URLMapper(all_url_mappings)
        await self._upsert_validated_flags(mapper)

    async def _lookup_urls(self) -> list[LookupURLForDataSourcesSyncResponse]:
        return await self.requester.lookup_urls(list(self.urls))

    async def _insert_agency_link(self, url_mappings: list[URLMapping]):
        link_url_agency_insert_params = self.param_manager.insert_agency_link(
            url_mappings
        )
        await self.requester.add_new_agency_links(link_url_agency_insert_params)

    async def _update_agency_link(self, lookups_existing_urls: list[LookupURLForDataSourcesSyncResponse]):
        link_url_agency_update_params = self.param_manager.update_agency_link(
            lookups_existing_urls
        )
        await self.requester.update_agency_links(link_url_agency_update_params)

    async def _add_new_data_sources(self, url_mappings: list[URLMapping]) -> None:
        url_ds_insert_params = self.param_manager.add_new_data_sources(url_mappings)
        await self.requester.add_new_data_sources(url_ds_insert_params)

    async def _add_new_urls(self, urls: list[str]) -> list[URLMapping]:
        url_insert_params: list[InsertURLForDataSourcesSyncParams] = self.param_manager.add_new_urls(urls)
        url_mappings = await self.requester.add_new_urls(url_insert_params)
        return url_mappings

    async def _update_existing_urls(self, lookups_existing_urls: list[LookupURLForDataSourcesSyncResponse]) -> None:
        update_params = self.param_manager.update_existing_urls(lookups_existing_urls)
        await self.requester.update_existing_urls(update_params)

    async def _upsert_validated_flags(self, url_mapper: URLMapper) -> None:
        flags: list[FlagURLValidatedPydantic] = self.param_manager.upsert_validated_flags(url_mapper)
        await self.requester.upsert_validated_flags(flags)