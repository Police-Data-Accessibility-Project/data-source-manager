from src.collectors.enums import URLStatus
from src.db.models.materialized_views.url_status.enums import URLStatusEnum
from src.external.pdap.enums import DataSourcesURLStatus


def convert_sm_url_status_to_ds_url_status(
    status_code: int
) -> DataSourcesURLStatus:
    match status_code:
        case 200:
            return DataSourcesURLStatus.OK
        case _:
            return DataSourcesURLStatus.BROKEN