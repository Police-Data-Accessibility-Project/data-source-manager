from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.add.core import AddMetaURLsQueryBuilder
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.convert import \
    convert_to_update_meta_urls_params, convert_url_lookups_to_url_mappings
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.filter import filter_existing_url_mappings, \
    filter_urls_to_add
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.lookup.core import LookupMetaURLsQueryBuilder
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.lookup.response import MetaURLLookupResponse
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.update.core import UpdateMetaURLsQueryBuilder
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.update.params import UpdateMetaURLsParams
from src.db.dtos.url.mapping import URLMapping
from src.db.templates.requester import RequesterBase


class UpdateMetaURLsRequester(RequesterBase):

    async def lookup_meta_urls(
        self,
        urls: list[str]
    ) -> list[MetaURLLookupResponse]:
        return await LookupMetaURLsQueryBuilder(
            urls
        ).run(self.session)

    async def add_new_urls_to_database(
        self,
        lookup_responses: list[MetaURLLookupResponse]
    ) -> list[URLMapping]:
        if len(lookup_responses) == 0:
            return []
        urls_to_add: list[str] = filter_urls_to_add(lookup_responses)
        if len(urls_to_add) == 0:
            return []
        return await AddMetaURLsQueryBuilder(urls_to_add).run(self.session)

    async def update_existing_urls(
        self,
        lookup_responses: list[MetaURLLookupResponse]
    ) -> list[URLMapping]:
        existing_url_lookups: list[MetaURLLookupResponse] = (
            filter_existing_url_mappings(lookup_responses)
        )
        params: list[UpdateMetaURLsParams] = \
            convert_to_update_meta_urls_params(existing_url_lookups)
        await UpdateMetaURLsQueryBuilder(params).run(self.session)
        existing_url_mappings: list[URLMapping] = \
            convert_url_lookups_to_url_mappings(existing_url_lookups)
        return existing_url_mappings

