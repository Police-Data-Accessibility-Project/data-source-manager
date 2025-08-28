from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.update.params import UpdateMetaURLsParams


def filter_urls_with_non_meta_record_type(
    params: list[UpdateMetaURLsParams]
) -> list[int]:
    raise NotImplementedError

def filter_urls_without_validation_flag(
    params: list[UpdateMetaURLsParams]
) -> list[int]:
    raise NotImplementedError

def filter_urls_with_non_meta_url_validation_flag(
    params: list[UpdateMetaURLsParams]
) -> list[int]:
    raise NotImplementedError