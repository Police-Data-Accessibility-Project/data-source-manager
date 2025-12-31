from src.external.pdap.enums import DataSourcesURLStatus


def convert_sm_url_status_to_ds_url_status(
    status_code: int
) -> DataSourcesURLStatus:
    match status_code:
        case 200:
            return DataSourcesURLStatus.OK
        case _:
            return DataSourcesURLStatus.BROKEN