from src.core.tasks.scheduled.impl.sync.data_sources.queries.upsert.url.lookup.response import URLDataSyncInfo
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.flag.url_validated.enums import ValidatedURLType
from src.external.pdap.enums import ApprovalStatus


def convert_url_sync_info_to_url_mappings(
    url_sync_info: URLDataSyncInfo
) -> URLMapping:
    return URLMapping(
        url=url_sync_info.url,
        url_id=url_sync_info.url_id
    )

def convert_approval_status_to_validated_type(
    approval_status: ApprovalStatus
) -> ValidatedURLType:
    match approval_status:
        case ApprovalStatus.APPROVED:
            return ValidatedURLType.DATA_SOURCE
        case ApprovalStatus.REJECTED:
            return ValidatedURLType.NOT_RELEVANT
        case _:
            raise ValueError(f"Invalid approval status: {approval_status}")