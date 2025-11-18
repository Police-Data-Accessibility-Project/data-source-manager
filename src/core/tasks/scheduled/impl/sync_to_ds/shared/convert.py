from src.collectors.enums import URLStatus
from src.external.pdap.enums import DataSourcesURLStatus


def convert_sm_url_status_to_ds_url_status(
    sm_url_status: URLStatus
) -> DataSourcesURLStatus:
    match sm_url_status:
        case URLStatus.OK:
            return DataSourcesURLStatus.OK
        case URLStatus.BROKEN:
            return DataSourcesURLStatus.BROKEN
        case _:
            raise ValueError(f"URL status has no corresponding DS Status: {sm_url_status}")