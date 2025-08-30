from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.lookup.response import MetaURLLookupResponse
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.update.params import UpdateMetaURLsParams
from src.db.dtos.url.mapping import URLMapping


def convert_to_update_meta_urls_params(
    lookups: list[MetaURLLookupResponse]
) -> list[UpdateMetaURLsParams]:
    return [
        UpdateMetaURLsParams(
            url_id=lookup.url_id,
            validation_type=lookup.validation_type,
            record_type=lookup.record_type,
        )
        for lookup in lookups
    ]

def convert_url_lookups_to_url_mappings(
    lookups: list[MetaURLLookupResponse]
) -> list[URLMapping]:
    return [
        URLMapping(
            url_id=lookup.url_id,
            url=lookup.url,
        )
        for lookup in lookups
    ]