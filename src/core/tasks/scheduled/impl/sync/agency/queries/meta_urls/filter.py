from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.lookup.response import AgencyMetaURLLookupResponse
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.models.subset import UpdateMetaAgenciesSubset
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


def filter_add_and_remove_meta_urls(
    lookup_responses: list[AgencyMetaURLLookupResponse],
    sync_responses: list[AgenciesSyncResponseInnerInfo]
) -> UpdateMetaAgenciesSubset: