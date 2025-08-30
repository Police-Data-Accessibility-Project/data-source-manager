from src.core.enums import RecordType
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.update.params import UpdateMetaURLsParams
from src.db.models.impl.flag.url_validated.enums import URLValidatedType


def filter_urls_with_non_meta_record_type(
    params: list[UpdateMetaURLsParams]
) -> list[int]:
    url_ids: list[int] = []
    for param in params:
        if param.record_type is None:
            url_ids.append(param.url_id)
        if param.record_type != RecordType.CONTACT_INFO_AND_AGENCY_META:
            url_ids.append(param.url_id)

    return url_ids

def filter_urls_without_validation_flag(
    params: list[UpdateMetaURLsParams]
) -> list[int]:
    url_ids: list[int] = []
    for param in params:
        if param.validation_type is None:
            url_ids.append(param.url_id)
    return url_ids

def filter_urls_with_non_meta_url_validation_flag(
    params: list[UpdateMetaURLsParams]
) -> list[int]:
    url_ids: list[int] = []
    for param in params:
        if param.validation_type is None:
            continue
        if param.validation_type != URLValidatedType.META_URL:
            url_ids.append(param.url_id)

    return url_ids